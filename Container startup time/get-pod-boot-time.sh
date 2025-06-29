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

initialized_time=$(get_condition_time Initialized)
ready_time=$(get_condition_time Ready)
containers_ready_time=$(get_condition_time ContainersReady)
pod_scheduled_time=$(get_condition_time PodScheduled)

# 각 단계별 소요 시간 계산 (소수점 셋째 자리까지)
Initialized_to_Ready=$(echo "$ready_time - $initialized_time" | bc)
Ready_to_ContainersReady=$(echo "$containers_ready_time - $ready_time" | bc)
ContainersReady_to_PodScheduled=$(echo "$pod_scheduled_time - $containers_ready_time" | bc)
All=$(echo "$pod_scheduled_time - $initialized_time" | bc)

# 결과 출력
printf "Initialized_to_Ready: %.3f seconds\n" $Initialized_to_Ready
printf "Ready_to_ContainersReady: %.3f seconds\n" $Ready_to_ContainersReady
printf "ContainersReady_to_PodScheduled: %.3f seconds\n" $ContainersReady_to_PodScheduled
printf "All: %.3f seconds\n" $All
