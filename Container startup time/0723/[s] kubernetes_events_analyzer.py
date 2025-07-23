# 초 단위로 이벤트 관찰

#!/usr/bin/env python3
import subprocess
import json
import time
from datetime import datetime
import threading

class KubernetesEventsAnalyzer:
    def __init__(self):
        self.pod_events = {}
        self.container_states = {}
        self.timing_analysis = {}
        
    def analyze_pod_startup(self):
        """Kubernetes 이벤트를 통한 파드 시작 분석"""
        
        print("=== Kubernetes Events Based Cold Startup Analysis ===")
        print("Environment: minikube -p istio with Bookinfo")
        
        # 1. 현재 상태 확인
        self.check_current_state()
        
        # 2. 이벤트 모니터링 시작
        self.start_event_monitoring()
        
        # 3. 순차적 파드 재시작
        self.restart_pods_sequentially()
        
        # 4. 분석 및 결과
        time.sleep(60)  # 충분한 안정화 시간
        self.generate_analysis()
    
    def check_current_state(self):
        """현재 파드 및 이벤트 상태 확인"""
        print("\nCurrent Bookinfo Pods Status:")
        
        result = subprocess.run([
            'kubectl', 'get', 'pods', '-o', 'wide'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # 헤더 제외
            for line in lines:
                if any(service in line for service in ['productpage', 'details', 'reviews', 'ratings']):
                    parts = line.split()
                    pod_name = parts[0]
                    ready = parts[1]
                    status = parts[2]
                    age = parts[4]
                    print(f"  {pod_name}: {ready} {status} (age: {age})")
    
    def start_event_monitoring(self):
        """Kubernetes 이벤트 실시간 모니터링"""
        print("\nStarting Kubernetes events monitoring...")
        
        def monitor_events():
            try:
                process = subprocess.Popen([
                    'kubectl', 'get', 'events', '--watch', '-o', 'json'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                for line in process.stdout:
                    try:
                        event = json.loads(line)
                        self.process_kubernetes_event(event)
                    except json.JSONDecodeError:
                        continue
            except Exception as e:
                print(f"Event monitoring error: {e}")
        
        monitor_thread = threading.Thread(target=monitor_events)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        time.sleep(3)  # 모니터링 안정화
    
    def process_kubernetes_event(self, event):
        """Kubernetes 이벤트 처리"""
        event_type = event.get('type', '')
        reason = event.get('reason', '')
        message = event.get('message', '')
        timestamp = event.get('firstTimestamp', event.get('eventTime', ''))
        
        involved_object = event.get('involvedObject', {})
        pod_name = involved_object.get('name', '')
        object_kind = involved_object.get('kind', '')
        
        # Pod 관련 이벤트만 처리
        if object_kind != 'Pod':
            return
            
        # Bookinfo 파드만 추적
        if not any(service in pod_name for service in ['productpage', 'details', 'reviews', 'ratings']):
            return
        
        timestamp_ms = self.parse_k8s_timestamp(timestamp)
        
        if pod_name not in self.pod_events:
            self.pod_events[pod_name] = []
        
        event_data = {
            'timestamp_ms': timestamp_ms,
            'reason': reason,
            'message': message,
            'type': event_type
        }
        
        self.pod_events[pod_name].append(event_data)
        
        # 중요한 이벤트만 출력
        important_reasons = ['Scheduled', 'Pulling', 'Pulled', 'Created', 'Started', 'Ready']
        if reason in important_reasons:
            service = self.extract_service_name(pod_name)
            print(f"[{timestamp_ms:.3f}ms] {service} - {reason}: {message[:50]}...")
    
    def parse_k8s_timestamp(self, timestamp_str):
        """Kubernetes 타임스탬프를 밀리초로 변환"""
        try:
            if 'T' in timestamp_str:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                return dt.timestamp() * 1000
        except:
            pass
        return time.time() * 1000
    
    def extract_service_name(self, pod_name):
        """파드 이름에서 서비스 이름 추출"""
        for service in ['productpage', 'details', 'reviews', 'ratings']:
            if service in pod_name:
                return service
        return 'unknown'
    
    def restart_pods_sequentially(self):
        """서비스별 순차적 파드 재시작"""
        services = ['productpage', 'details', 'ratings', 'reviews']
        
        print("\n=== Sequential Pod Restart for Cold Start Analysis ===")
        
        for service in services:
            print(f"\nRestarting {service} service...")
            
            # 재시작 시작 시간 기록
            restart_start = time.time() * 1000
            
            # 파드 삭제
            subprocess.run(['kubectl', 'delete', 'pods', '-l', f'app={service}'])
            
            # 파드 준비 대기
            try:
                subprocess.run([
                    'kubectl', 'wait', '--for=condition=ready', 'pod',
                    '-l', f'app={service}', '--timeout=120s'
                ], check=True)
                
                restart_end = time.time() * 1000
                restart_duration = restart_end - restart_start
                
                print(f"{service} restart completed in {restart_duration:.3f}ms")
                
                # 새 파드 상세 분석
                self.analyze_new_pods(service, restart_start)
                
            except subprocess.CalledProcessError:
                print(f"Timeout waiting for {service} to be ready")
            
            time.sleep(10)  # 다음 재시작 전 대기
    
    def analyze_new_pods(self, service, restart_start_time):
        """새로 생성된 파드의 상세 분석"""
        try:
            # 해당 서비스의 새 파드 정보 가져오기
            result = subprocess.run([
                'kubectl', 'get', 'pods', '-l', f'app={service}', '-o', 'json'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                pods_data = json.loads(result.stdout)
                
                for pod in pods_data['items']:
                    pod_name = pod['metadata']['name']
                    creation_time = pod['metadata']['creationTimestamp']
                    
                    # 컨테이너 상태 분석
                    self.analyze_container_startup_times(pod_name, pod, restart_start_time)
                    
        except Exception as e:
            print(f"Error analyzing new pods for {service}: {e}")
    
    def analyze_container_startup_times(self, pod_name, pod_data, restart_start):
        """개별 컨테이너의 시작 시간 분석"""
        
        # 파드 생성 시간
        creation_timestamp = pod_data['metadata']['creationTimestamp']
        creation_time_ms = self.parse_k8s_timestamp(creation_timestamp)
        
        # 컨테이너 상태 정보
        container_statuses = pod_data.get('status', {}).get('containerStatuses', [])
        
        analysis = {
            'pod_name': pod_name,
            'service': self.extract_service_name(pod_name),
            'restart_start_ms': restart_start,
            'pod_creation_ms': creation_time_ms,
            'scheduling_delay_ms': creation_time_ms - restart_start,
            'containers': []
        }
        
        for container in container_statuses:
            container_name = container['name']
            is_ready = container.get('ready', False)
            restart_count = container.get('restartCount', 0)
            
            container_analysis = {
                'name': container_name,
                'ready': is_ready,
                'restart_count': restart_count,
                'is_sidecar': container_name == 'istio-proxy'
            }
            
            # 실행 상태 정보
            if 'state' in container and 'running' in container['state']:
                started_at = container['state']['running'].get('startedAt', '')
                if started_at:
                    started_time_ms = self.parse_k8s_timestamp(started_at)
                    container_analysis['started_at_ms'] = started_time_ms
                    container_analysis['startup_delay_ms'] = started_time_ms - creation_time_ms
            
            analysis['containers'].append(container_analysis)
        
        # 전체 준비 시간 계산
        if all(c['ready'] for c in analysis['containers']):
            current_time = time.time() * 1000
            analysis['total_ready_time_ms'] = current_time - restart_start
        
        self.timing_analysis[pod_name] = analysis
        
        # 즉시 출력
        print(f"\n*** {pod_name} TIMING ANALYSIS ***")
        print(f"Service: {analysis['service']}")
        print(f"Scheduling Delay: {analysis['scheduling_delay_ms']:.3f}ms")
        
        for container in analysis['containers']:
            container_type = "Sidecar" if container['is_sidecar'] else "Main App"
            startup_time = container.get('startup_delay_ms', 0)
            print(f"  {container['name']} ({container_type}): {startup_time:.3f}ms")
        
        if 'total_ready_time_ms' in analysis:
            print(f"Total Ready Time: {analysis['total_ready_time_ms']:.3f}ms")
    
    def generate_analysis(self):
        """최종 분석 결과 생성"""
        print("\n" + "="*60)
        print("KUBERNETES EVENTS BASED COLD STARTUP ANALYSIS")
        print("="*60)
        
        if not self.timing_analysis:
            print("❌ No timing analysis data collected")
            return
        
        # 서비스별 분석
        service_data = {}
        for pod_name, analysis in self.timing_analysis.items():
            service = analysis['service']
            if service not in service_data:
                service_data[service] = []
            service_data[service].append(analysis)
        
        # 서비스별 통계
        for service, analyses in service_data.items():
            print(f"\n🔹 {service.upper()} SERVICE ANALYSIS:")
            
            # 스케줄링 지연
            scheduling_delays = [a['scheduling_delay_ms'] for a in analyses if 'scheduling_delay_ms' in a]
            if scheduling_delays:
                avg_scheduling = sum(scheduling_delays) / len(scheduling_delays)
                print(f"  Average Scheduling Delay: {avg_scheduling:.3f}ms")
            
            # 컨테이너별 분석
            main_containers = []
            sidecar_containers = []
            
            for analysis in analyses:
                for container in analysis['containers']:
                    startup_time = container.get('startup_delay_ms', 0)
                    if container['is_sidecar']:
                        sidecar_containers.append(startup_time)
                    else:
                        main_containers.append(startup_time)
            
            if main_containers:
                avg_main = sum(main_containers) / len(main_containers)
                print(f"  Average Main Container Startup: {avg_main:.3f}ms")
            
            if sidecar_containers:
                avg_sidecar = sum(sidecar_containers) / len(sidecar_containers)
                print(f"  Average Sidecar Startup: {avg_sidecar:.3f}ms")
            
            # 전체 준비 시간
            total_times = [a.get('total_ready_time_ms', 0) for a in analyses if 'total_ready_time_ms' in a]
            if total_times:
                avg_total = sum(total_times) / len(total_times)
                print(f"  Average Total Ready Time: {avg_total:.3f}ms")
        
        # 결과 저장
        output_data = {
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_method': 'kubernetes_events',
            'environment': 'minikube-istio-bookinfo',
            'pod_events': self.pod_events,
            'timing_analysis': self.timing_analysis,
            'service_statistics': service_data
        }
        
        with open('kubernetes_events_cold_start_analysis.json', 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: kubernetes_events_cold_start_analysis.json")
        print("✅ Analysis Complete!")

if __name__ == "__main__":
    analyzer = KubernetesEventsAnalyzer()
    analyzer.analyze_pod_startup()
