/*
 * Copyright 2012-2014 Narantech Inc. All rights reserved.
 *  __    _ _______ ______   _______ __    _ _______ _______ _______ __   __
 * |  |  | |   _   |    _ | |   _   |  |  | |       |       |       |  | |  |
 * |   |_| |  |_|  |   | || |  |_|  |   |_| |_     _|    ___|       |  |_|  |
 * |       |       |   |_||_|       |       | |   | |   |___|       |       |
 * |  _    |       |    __  |       |  _    | |   | |    ___|      _|       |
 * | | |   |   _   |   |  | |   _   | | |   | |   | |   |___|     |_|   _   |
 * |_|  |__|__| |__|___|  |_|__| |__|_|  |__| |___| |_______|_______|__| |__|
 *
 * The nfs main.
 */

(function() {
    var INIT_COUNT = 2;
    var initializedCount = 0;
    var api = new $.ApiWeb('apis');

    // init handlers.
    api.on('ready', function(a) {
        _handleInit();
    });

    $(window).ready(function() {
        _handleInit();
    });

    // TODO: start app loading here.
    $('.login').hide();

    function clearPassword() {
        setEnablePanel(false);
        $('#password')[0].value = "";
        $('#password-new')[0].value = "";
        $('#password-new-again')[0].value = "";
        console.log("Clear");
    }

    function setEnablePanel(visibility) {
        if (visibility) {
            $("#modal")[0].style.visibility = "visible";
            $("#loader-container")[0].style.visibility = "visible";
            console.log("Modal loader state is visible");
        } else {
            $("#modal")[0].style.visibility = "hidden";
            $("#loader-container")[0].style.visibility = "hidden";
            console.log("Modal loader state is hidden");
        }
    }

    function _buildView() {
        // build view.
        $('#username').val('nfs');
        $('#username').attr('readonly', true);
        // init button handler.
        $('#submit_btn').click(function() {
            setEnablePanel(true);
            var cur = $('#password').val().trim();
            var pwd = $('#password-new').val().trim();
            var pwd2 = $('#password-new-again').val().trim();

            if (!cur || !pwd || !pwd2) {
                _showError('Please fill out the password.');
                clearPassword();
                console.warn('Failed to change password, given passsword is empty.');
                return;
            }

            if (pwd === pwd2) {
                api.set_password(cur, pwd)(function(ret) {
                    if (ret) {
                        _showFeedback('Password change successed.');
                        _hideHelpPage();
                    } else {
                        _showError("Error while changing the password.");
                    }
                    clearPassword();
                });
            } else {
                console.log("Passwords do not match.");
                _showError("Passwords do not match.");
                clearPassword();
            }
        });
    }

    function _showHelpPage(defaultPassword) {
        var container = $('<div/>', {
            class: 'help-message-container'
        });
        var messageLabel = $('<div/>', {
            class: 'help-message-label',
            html: '<ul><li><label>Note</label></li><li>Access your data over the network as if they are your local drive.</li>' +
                '<li><span class="help-message-container-id">\'nfs\'</span> is your account ID that cannot be changed.</li>' +
                '<li><span class="help-message-container-password">' + defaultPassword +
                '</span> is your current password. When it is changed, this message will no longer be shown.</li></ul>'
        });
        container.append(messageLabel);
        $('body').append(container);
    }

    function _hideHelpPage() {
        $('.help-message-container').remove();
    }

    function _handleInit() {
        if (++initializedCount >= INIT_COUNT) {
            _buildView();
            if (api.cache.has_password) {
                console.debug('Detected has password. display ui.');
                $('.login').show();
            } else {
                console.debug('The user do not set password yet. display help page.');
                _showHelpPage(api.cache.default_password);
            }
        }
    }

    function _showError(message) {
        $('.feedback-label').removeClass('disabled').removeClass('info').addClass('error').text(message);
    }

    function _showFeedback(message) {
        $('.feedback-label').removeClass('disabled').removeClass('error').addClass('info').text(message);
    }

    function _clearFeedback() {
        $('.feedback-label').removeClass('info error').addClass('disabled').text('');
    }
})();