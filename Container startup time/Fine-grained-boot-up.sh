### Fine-grained measurement

#!/usr/bin/env bash

pod="$1"

get_time() {
    condition="$1"
    iso_time=$(kubectl get pod "$pod" -o json | jq -r ".status.conditions[] | select(.type == \"$condition\" and .status == \"True\") | .lastTransitionTime")
    # ISO8601 → 초.나노초 변환
    date -d "$iso_time" +"%s.%N"
}

pod_scheduled_time=$(get_time PodScheduled)
initialized_time=$(get_time Initialized)
containers_ready_time=$(get_time ContainersReady)
ready_time=$(get_time Ready)

# 단계별 소요 시간(밀리초 단위, 소수점 셋째 자리까지)
scheduled_to_initialized=$(echo "$initialized_time - $pod_scheduled_time" | bc)
initialized_to_containers_ready=$(echo "$containers_ready_time - $initialized_time" | bc)
containers_ready_to_ready=$(echo "$ready_time - $containers_ready_time" | bc)
scheduled_to_ready=$(echo "$ready_time - $pod_scheduled_time" | bc)

printf "PodScheduled → Initialized: %.3f sec\n" $scheduled_to_initialized
printf "Initialized → ContainersReady: %.3f sec\n" $initialized_to_containers_ready
printf "ContainersReady → Ready: %.3f sec\n" $containers_ready_to_ready
printf "PodScheduled → Ready: %.3f sec\n" $scheduled_to_ready
