### measuring startup time
## get-pod-boot-time.sh

#!/usr/bin/env bash

pod="$1"

get_condition_time() {
    condition="$1"
    iso_time=$(kubectl get pod "$pod" -o json | jq ".status.conditions[] | select(.type == \"$condition\" and .status == \"True\") | .lastTransitionTime" | tr -d '"\n')
    date -d $iso_time +%s
}

initialized_time=$(get_condition_time PodScheduled)
ready_time=$(get_condition_time Ready)
duration_seconds=$(( ready_time - initialized_time ))

echo "It took $duration_seconds seconds for $pod to boot up"
