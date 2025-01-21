<script src="https://webgazer.cs.brown.edu/webgazer.js"></script>
<script>
    function startGazeTracking() {
        webgazer.setGazeListener(function(data, timestamp) {
            if (data != null) {
                console.log({x: data.x, y: data.y, timestamp: timestamp});
            }
        }).begin();
    }
    startGazeTracking();
</script>