# pod삭제 후 재설치는 warm start 이므로, deployment/replicaset을 제거한 후
# pod를 재배포해야 cold start time을 측정가능함(수정예정)

import subprocess
import json
import time
from datetime import datetime
import threading
import re

class DetailedStartupAnalyzer:
    def __init__(self):
        self.pod_lifecycle = {}
        self.container_states = {}
        self.detailed_analysis = {}
        
    def analyze_startup_stages(self, service_name):
        """특정 서비스의 상세 시작 단계 분석"""
        
        print(f"\n=== Analyzing {service_name} Container Startup Stages ===")
        
        # 1. 현재 파드 삭제 및 이벤트 모니터링 시작
        self.start_event_monitoring()
        
        # 2. 파드 삭제
        start_time = time.time() * 1000  # ms 단위
        self.delete_service_pods(service_name)
        
        # 3. 상세 단계별 추적
        self.track_detailed_stages(service_name, start_time)
        
        # 4. 분석 결과 출력
        self.generate_detailed_report(service_name)
    
    def start_event_monitoring(self):
        """Kubernetes 이벤트 실시간 모니터링"""
        print("Starting Kubernetes events monitoring...")
        
        def monitor_events():
            try:
                process = subprocess.Popen([
                    'kubectl', 'get', 'events', '--watch', '-o', 'json'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                for line in process.stdout:
                    try:
                        event = json.loads(line)
                        self.process_k8s_event(event)
                    except json.JSONDecodeError:
                        continue
            except Exception as e:
                print(f"Event monitoring error: {e}")
        
        monitor_thread = threading.Thread(target=monitor_events)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def process_k8s_event(self, event):
        """Kubernetes 이벤트 처리"""
        if event.get('type') != 'Normal':
            return
            
        reason = event.get('reason', '')
        message = event.get('message', '')
        timestamp = event.get('firstTimestamp', event.get('eventTime', ''))
        involved_object = event.get('involvedObject', {})
        
        pod_name = involved_object.get('name', '')
        
        # Bookinfo 관련 이벤트만 처리
        if not any(service in pod_name for service in ['productpage', 'details', 'reviews', 'ratings']):
            return
        
        timestamp_ms = self.parse_k8s_timestamp(timestamp)
        
        if pod_name not in self.pod_lifecycle:
            self.pod_lifecycle[pod_name] = {}
        
        # 주요 생명주기 이벤트 매핑
        lifecycle_events = {
            'Scheduled': 'pod_scheduled',
            'Pulling': 'image_pulling',
            'Pulled': 'image_pulled', 
            'Created': 'container_created',
            'Started': 'container_started',
            'Ready': 'pod_ready'
        }
        
        if reason in lifecycle_events:
            stage = lifecycle_events[reason]
            self.pod_lifecycle[pod_name][stage] = {
                'timestamp_ms': timestamp_ms,
                'message': message
            }
            
            print(f"[{timestamp_ms:.3f}ms] {pod_name} - {stage}: {message}")
    
    def parse_k8s_timestamp(self, timestamp_str):
        """Kubernetes 타임스탬프를 밀리초로 변환"""
        try:
            if 'T' in timestamp_str:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                return dt.timestamp() * 1000
        except:
            pass
        return time.time() * 1000
    
    def delete_service_pods(self, service_name):
        """서비스 파드 삭제"""
        print(f"Deleting {service_name} pods...")
        subprocess.run(['kubectl', 'delete', 'pods', '-l', f'app={service_name}'])
    
    def track_detailed_stages(self, service_name, start_time):
        """상세 단계별 추적"""
        print(f"Tracking detailed startup stages for {service_name}...")
        
        # Pod 생성 대기
        time.sleep(2)
        
        # 새로 생성된 파드 찾기
        result = subprocess.run([
            'kubectl', 'get', 'pods', '-l', f'app={service_name}', 
            '-o', 'json'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Failed to get {service_name} pods")
            return
        
        pods_data = json.loads(result.stdout)
        
        for pod in pods_data['items']:
            pod_name = pod['metadata']['name']
            creation_time = pod['metadata']['creationTimestamp']
            
            print(f"\nAnalyzing pod: {pod_name}")
            
            # 상세 컨테이너 상태 추적
            self.track_container_states(pod_name, start_time)
            
            # 파드가 Ready 상태가 될 때까지 대기하며 추적
            self.wait_and_track_ready_state(pod_name)
    
    def track_container_states(self, pod_name, start_time):
        """개별 컨테이너 상태 상세 추적"""
        
        container_analysis = {
            'pod_name': pod_name,
            'start_tracking_time': start_time,
            'containers': {}
        }
        
        # 30초 동안 상태 변화 추적
        for i in range(30):
            try:
                result = subprocess.run([
                    'kubectl', 'get', 'pod', pod_name, '-o', 'json'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    pod_data = json.loads(result.stdout)
                    current_time = time.time() * 1000
                    
                    # 컨테이너 상태 정보 수집
                    container_statuses = pod_data.get('status', {}).get('containerStatuses', [])
                    
                    for container in container_statuses:
                        container_name = container['name']
                        
                        if container_name not in container_analysis['containers']:
                            container_analysis['containers'][container_name] = {
                                'states_history': []
                            }
                        
                        # 현재 상태 기록
                        state_info = {
                            'timestamp_ms': current_time,
                            'elapsed_ms': current_time - start_time,
                            'ready': container.get('ready', False),
                            'restart_count': container.get('restartCount', 0),
                            'state': {}
                        }
                        
                        # 상태별 상세 정보
                        if 'state' in container:
                            for state_type in ['waiting', 'running', 'terminated']:
                                if state_type in container['state']:
                                    state_details = container['state'][state_type]
                                    state_info['state'][state_type] = state_details
                                    
                                    if state_type == 'waiting':
                                        reason = state_details.get('reason', '')
                                        print(f"[{current_time:.3f}ms] {pod_name}/{container_name} - Waiting: {reason}")
                                    elif state_type == 'running':
                                        started_at = state_details.get('startedAt', '')
                                        print(f"[{current_time:.3f}ms] {pod_name}/{container_name} - Running since: {started_at}")
                        
                        container_analysis['containers'][container_name]['states_history'].append(state_info)
                
            except Exception as e:
                print(f"Error tracking container states: {e}")
            
            time.sleep(1)  # 1초마다 상태 확인
        
        self.container_states[pod_name] = container_analysis
    
    def wait_and_track_ready_state(self, pod_name):
        """파드 Ready 상태까지의 상세 추적"""
        print(f"Waiting for {pod_name} to become ready...")
        
        try:
            # Ready 상태까지 대기 (최대 5분)
            result = subprocess.run([
                'kubectl', 'wait', '--for=condition=ready', 'pod', pod_name, '--timeout=300s'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                ready_time = time.time() * 1000
                print(f"[{ready_time:.3f}ms] {pod_name} - Ready!")
                
                # 최종 상태 정보 수집
                self.collect_final_state_info(pod_name, ready_time)
            else:
                print(f"Timeout waiting for {pod_name} to become ready")
                
        except Exception as e:
            print(f"Error waiting for ready state: {e}")
    
    def collect_final_state_info(self, pod_name, ready_time):
        """최종 상태 정보 수집"""
        try:
            # 파드 상세 정보
            result = subprocess.run([
                'kubectl', 'describe', 'pod', pod_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                describe_output = result.stdout
                
                # 중요한 타이밍 정보 추출
                events_section = self.extract_events_from_describe(describe_output)
                
                if pod_name not in self.detailed_analysis:
                    self.detailed_analysis[pod_name] = {}
                
                self.detailed_analysis[pod_name]['final_state'] = {
                    'ready_time_ms': ready_time,
                    'events': events_section
                }
                
        except Exception as e:
            print(f"Error collecting final state: {e}")
    
    def extract_events_from_describe(self, describe_output):
        """kubectl describe 출력에서 이벤트 추출"""
        events = []
        in_events_section = False
        
        for line in describe_output.split('\n'):
            if 'Events:' in line:
                in_events_section = True
                continue
            
            if in_events_section and line.strip():
                # 이벤트 라인 파싱
                if re.match(r'^\s+\w+\s+\w+\s+\d+', line):
                    events.append(line.strip())
        
        return events
    
    def generate_detailed_report(self, service_name):
        """상세 분석 리포트 생성"""
        print(f"\n=== {service_name.upper()} DETAILED STARTUP ANALYSIS ===")
        
        service_pods = [pod for pod in self.container_states.keys() 
                       if service_name in pod]
        
        for pod_name in service_pods:
            print(f"\nPod: {pod_name}")
            
            pod_data = self.container_states[pod_name]
            containers = pod_data['containers']
            
            for container_name, container_data in containers.items():
                print(f"\n  Container: {container_name}")
                
                states_history = container_data['states_history']
                if not states_history:
                    continue
                
                # 주요 상태 변화 시점 분석
                waiting_to_running = None
                running_to_ready = None
                
                for i, state in enumerate(states_history):
                    if i > 0:
                        prev_state = states_history[i-1]
                        
                        # Waiting -> Running 전환 감지
                        if ('waiting' in prev_state['state'] and 
                            'running' in state['state'] and 
                            waiting_to_running is None):
                            waiting_to_running = state['elapsed_ms']
                            print(f"    Waiting -> Running: {waiting_to_running:.3f}ms")
                        
                        # Running -> Ready 전환 감지
                        if (not prev_state['ready'] and state['ready'] and 
                            running_to_ready is None):
                            running_to_ready = state['elapsed_ms']
                            print(f"    Running -> Ready: {running_to_ready:.3f}ms")
                
                # 총 시작 시간
                final_state = states_history[-1]
                if final_state['ready']:
                    total_time = final_state['elapsed_ms']
                    print(f"    Total startup time: {total_time:.3f}ms")
                    
                    # 단계별 비율 계산
                    if waiting_to_running and running_to_ready:
                        image_pull_time = waiting_to_running
                        startup_time = running_to_ready - waiting_to_running
                        
                        print(f"    Breakdown:")
                        print(f"      Image pull & container creation: {image_pull_time:.3f}ms ({image_pull_time/total_time*100:.1f}%)")
                        print(f"      Application startup: {startup_time:.3f}ms ({startup_time/total_time*100:.1f}%)")
        
        # 결과를 JSON으로 저장
        output_data = {
            'service': service_name,
            'analysis_timestamp': datetime.now().isoformat(),
            'pod_lifecycle': self.pod_lifecycle,
            'container_states': self.container_states,
            'detailed_analysis': self.detailed_analysis
        }
        
        filename = f'{service_name}_detailed_startup_analysis.json'
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\nDetailed analysis saved to: {filename}")

if __name__ == "__main__":
    analyzer = DetailedStartupAnalyzer()
    
    # 분석할 서비스 선택
    service = input("Enter service name to analyze (productpage/details/reviews/ratings): ").strip()
    
    if service in ['productpage', 'details', 'reviews', 'ratings']:
        analyzer.analyze_startup_stages(service)
    else:
        print("Invalid service name. Please choose from: productpage, details, reviews, ratings")
