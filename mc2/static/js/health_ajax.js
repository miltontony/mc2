// Get the health data from server every 5 seconds
$(document).ready(function () {
    interval_timer = setInterval(refreshHealth, 10000);
});

/**
 * Build the html <div> tag to replace the old <div> on the page
 * @param status json object with the health data for the given app
 */
function buildHTML(status) {
    /*
     data = {
     "instances": 3,
     "running": 3,
     "unhealthy": 0,
     "error": false,
     "healthy": 3,
     "health_defined": true,
     "staged": 0,
     "app_id": "small-dawn-617",
     "deploying": false
     }
     */
    var div_tag = '<div class="widget-user-desc" id="status-' + status.app_id + '">' +
        '<strong>' + status.app_id + '</strong>';

    if (!status.error) {
        if (status.deploying) {
            div_tag += '(App is being deployed)';
        }
        div_tag += '<br/>';
        if (status.instances == 0) {
            div_tag += 'There are no running instances of this app!<br/>';
        } else {
            // There are running instances of the app
            div_tag += 'Running instances: ' + status.running + ' of ' + status.instances;

            // Check if there are any staged apps
            if (status.staged > 0) {
                div_tag += '(' + status.staged + ' staged)';
            }
            div_tag += '<br/>';

            if (status.health_defined) {
                if (status.healthy != 0) { div_tag += ' <span class="label bg-green">' + status.healthy + ' healthy</span>';}
                if (status.unhealthy != 0){ div_tag +=' <span class="label bg-red">' + status.unhealthy + ' unhealthy</span><br/>';}
            } else {
                div_tag += '<span class="label bg-orange">Health check not defined!</span><br/>'
            }
        }
    } else {
        // There's an error
        div_tag += '<br/><span class="label bg-orange">Unable to retrieve health data</span>';
    }
    div_tag += '</div>';
    return div_tag;

}

function processData(data, textStatus, xhr) {
    if (xhr.status == 200) {
        if (!data.error) {
            for (var i = 0; i < data.apps_health.length; i++) {
                app_health = data.apps_health[i];
                var tag_id = '#status-' + app_health.app_id;
                div = $(buildHTML(app_health));
                $(tag_id).replaceWith(div);
            }
        }
    }
    else {
        console.log('Request to get data failed: Error-' + xhr.status);
        clearInterval(interval_timer);
        console.log('Could not retrieve health data from server.')
    }
}

function getHealthError(data) {
    // stop the health requests and tell the user
    clearInterval(interval_timer);
    console.log('Could not retrieve health data from server.')
}

/**
 * Function to get health status from the server and update the apps on the page
 */
function refreshHealth() {
    $.ajax({
        type: 'GET',
        url: 'v2/apps/health/',
        success: processData,
        error: getHealthError,
        timeout: 20000
    });
}
