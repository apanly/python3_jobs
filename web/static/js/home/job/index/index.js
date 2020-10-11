;
var jon_index_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        $(".job_list_wrap .ops").click(function () {
            var btn_target = $("this");
            if (btn_target.hasClass("disabled")) {
                common_ops.alert("正在保存，请不要重复提交~~");
                return false;
            }
            var data = {
                'id': $(this).data('id'),
                'act': $(this).data('act')
            };
            var callback = {
                "ok": function () {
                    $.ajax({
                        url: home_common_ops.buildUrl('/job/index/ops'),
                        data: data,
                        type: 'POST',
                        dataType: 'json',
                        success: function (res) {
                            btn_target.removeClass("disabled");
                            var callback = {};
                            if (res.code == 200) {
                                callback = function () {
                                    window.location.href = window.location.href;
                                }
                            }
                            common_ops.msg(res.msg, res.code == 200, callback);
                        }
                    });
                }
            };

            var msg = "确认设置为 " + $(this).text() + " ?" ;
            var desc = $(this).data('title');
            if( desc != undefined ){
                msg += "<br/>" + desc;
            }

            common_ops.confirm(msg, callback);
        });
    }
};

$(document).ready(function () {
    jon_index_ops.init();
});