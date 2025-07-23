# 각 서비스 별 pod 시작 시간 및 istio-proxy 시작 시간
# PRODUCTPAGE:
# Total Cold Start Time: 5822.654ms
# Pod Creation: 5822.654ms
# Main Container Ready: 5822.654ms
# Sidecar Ready: 5822.654ms
# Container Ready 시간과 Sidecar Ready 시간이 동일하게 나오는 문제 해결 필요함

import subprocess
import time
import json
from datetime import datetime

class RealtimePodTracker:
    def __init__(self):
        self.measurements = {}
        
    def track_single_service_restart(self, service):
        """단일 서비스의 상세 재시작 추적"""
        
        print(f"=== Tracking {service} Cold Startup ===")
        
        # 1. 시작 시간 기록
        start_time = time.time() * 1000
        print(f"Start time: {start_time:.3f}ms")
        
        # 2. 파드 삭제
        print("Deleting existing pods...")
        subprocess.run(['kubectl', 'delete', 'pods', '-l', f'app={service}'])
        
        # 3. 실시간 상태 추적
        stages = {}
        
        # 파드 생성 감지
        pod_created = False
        containers_ready = False
        
        for i in range(120):  # 최대 2분 추적
            current_time = time.time() * 1000
            elapsed = current_time - start_time
            
            try:
                # 파드 상태 확인
                result = subprocess.run([
                    'kubectl', 'get', 'pods', '-l', f'app={service}', 
                    '-o', 'json'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    pods_data = json.loads(result.stdout)
                    
                    if pods_data['items'] and not pod_created:
                        pod_created = True
                        stages['pod_created'] = elapsed
                        pod_name = pods_data['items'][0]['metadata']['name']
                        print(f"[{elapsed:.3f}ms] Pod created: {pod_name}")
                    
                    if pods_data['items']:
                        pod = pods_data['items'][0]
                        
                        # 컨테이너 상태 확인
                        container_statuses = pod.get('status', {}).get('containerStatuses', [])
                        
                        for container in container_statuses:
                            container_name = container['name']
                            ready = container.get('ready', False)
                            
                            stage_key = f"{container_name}_ready"
                            if ready and stage_key not in stages:
                                stages[stage_key] = elapsed
                                container_type = "sidecar" if container_name == "istio-proxy" else "main"
                                print(f"[{elapsed:.3f}ms] {container_name} ({container_type}) ready")
                        
                        # 모든 컨테이너 준비 확인
                        all_ready = all(c.get('ready', False) for c in container_statuses)
                        if all_ready and not containers_ready:
                            containers_ready = True
                            stages['all_containers_ready'] = elapsed
                            print(f"[{elapsed:.3f}ms] All containers ready!")
                            break
            
            except Exception as e:
                print(f"Error at {elapsed:.3f}ms: {e}")
            
            time.sleep(1)
        
        # 4. 결과 분석
        self.measurements[service] = {
            'service': service,
            'start_time': start_time,
            'stages': stages,
            'total_time': elapsed if containers_ready else None
        }
        
        print(f"\n*** {service.upper()} COLD START BREAKDOWN ***")
        prev_time = 0
        for stage, timestamp in sorted(stages.items(), key=lambda x: x[1]):
            duration = timestamp - prev_time
            print(f"  {stage}: {timestamp:.3f}ms (+{duration:.3f}ms)")
            prev_time = timestamp
        
        return stages
    
    def analyze_all_services(self):
        """모든 Bookinfo 서비스 분석"""
        services = ['productpage', 'details', 'ratings', 'reviews']
        
        print("=== Realtime Pod Tracking Analysis ===")
        
        for service in services:
            self.track_single_service_restart(service)
            time.sleep(10)  # 서비스 간 대기
        
        # 최종 분석
        self.generate_comparison()
    
    def generate_comparison(self):
        """서비스 간 비교 분석"""
        print("\n" + "="*60)
        print("SERVICES COMPARISON ANALYSIS")
        print("="*60)
        
        for service, data in self.measurements.items():
            stages = data['stages']
            total_time = data.get('total_time', 0)
            
            print(f"\n{service.upper()}:")
            print(f"  Total Cold Start Time: {total_time:.3f}ms")
            
            # 주요 단계 시간 추출
            if 'pod_created' in stages:
                print(f"  Pod Creation: {stages['pod_created']:.3f}ms")
            
            main_ready = next((v for k, v in stages.items() 
                             if 'ready' in k and 'istio-proxy' not in k), None)
            if main_ready:
                print(f"  Main Container Ready: {main_ready:.3f}ms")
            
            sidecar_ready = stages.get('istio-proxy_ready')
            if sidecar_ready:
                print(f"  Sidecar Ready: {sidecar_ready:.3f}ms")
        
        # JSON 저장
        output_data = {
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_method': 'realtime_tracking',
            'environment': 'minikube-istio-bookinfo',
            'measurements': self.measurements
        }
        
        with open('realtime_pod_tracking_results.json', 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\nResults saved to: realtime_pod_tracking_results.json")

if __name__ == "__main__":
    tracker = RealtimePodTracker()
    tracker.analyze_all_services()
