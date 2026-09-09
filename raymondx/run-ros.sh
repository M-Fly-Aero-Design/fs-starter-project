#!/usr/bin/env bash
# Open a ROS 2 Humble shell for this repo, using Docker instead of a VM.
#
#   ./raymondx/run-ros.sh          # drop into a ROS shell
#   ./raymondx/run-ros.sh build    # colcon build the raymondx package
#   ./raymondx/run-ros.sh test     # colcon build + test + show results
#
# Run it once per terminal -- open two terminals to run flash and thunder
# side by side:
#   terminal 1:  ros2 run raymondx flash
#   terminal 2:  ros2 run raymondx thunder
set -euo pipefail

CONTAINER=mfly-ros
IMAGE=ros:humble
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MOUNT=/root/ros2_ws/src/fs-starter-project

if ! docker info >/dev/null 2>&1; then
  echo "Docker isn't running. Start Docker Desktop, then try again." >&2
  exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
  echo "Starting $CONTAINER from $IMAGE ..."
  docker run -d --name "$CONTAINER" -v "$REPO:$MOUNT" -w /root/ros2_ws \
    "$IMAGE" sleep infinity >/dev/null
fi

SETUP='source /opt/ros/humble/setup.bash
export ROS_LOCALHOST_ONLY=1
cd /root/ros2_ws
[ -f install/setup.bash ] && source install/setup.bash'

case "${1:-shell}" in
  build)
    docker exec "$CONTAINER" bash -lc "$SETUP; colcon build --packages-select raymondx"
    ;;
  test)
    docker exec "$CONTAINER" bash -lc \
      "$SETUP; colcon build --packages-select raymondx && \
       colcon test --packages-select raymondx; colcon test-result --all --verbose"
    ;;
  shell)
    echo "ROS 2 Humble shell. Try: ros2 run raymondx flash"
    docker exec -it "$CONTAINER" bash -lc "$SETUP; exec bash"
    ;;
  *)
    echo "usage: $0 [shell|build|test]" >&2
    exit 1
    ;;
esac
