### measuring startup time
## get-pod-boot-time.sh

#!/usr/bin/env bash

pod="$1"

get_condition_time() {
    condition="$1"
    iso_time=$(kubectl get pod "$pod" -o json | jq ".status.conditions[] | select(.type == \"$condition\" and .status == \"True\") | .lastTransitionTime" | tr -d '"\n')
    # ISO8601 타임스탬프를 초.나노초 단위로 변환
    date -d $iso_time +%s.%N
}

pod_scheduled_time=$(get_condition_time PodScheduled)
initialized_time=$(get_condition_time Initialized)
ready_time=$(get_condition_time Ready)
containers_ready_time=$(get_condition_time ContainersReady)

# 각 단계별 소요 시간 계산 (소수점 셋째 자리까지)
scheduled_to_initialized=$(echo "$initialized_time - $pod_scheduled_time" | bc)
initialized_to_ready=$(echo "$ready_time - $initialized_time" | bc)
ready_to_containers_ready=$(echo "$containers_ready_time - $ready_time" | bc)

# 결과 출력
printf "PodScheduled to Initialized: %.3f seconds\n" $scheduled_to_initialized
printf "Initialized to Ready: %.3f seconds\n" $initialized_to_ready
printf "Ready to ContainersReady: %.3f seconds\n" $ready_to_containers_ready
