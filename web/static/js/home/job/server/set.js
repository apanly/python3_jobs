;
var server_set_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        var that = this;
        $(".server_set_wrap select[name='env[]']").select2({
            language: "zh-CN",
            width: '100%',
            placeholder: '请选择支持环境'
        });
        $(".server_set_wrap .save").click(function () {
            var btn_target = $(this);
            if (btn_target.hasClass("disabled")) {
                common_ops.alert("正在保存，请不要重复提交~~");
                return false;
            }


            var name_target = $(".server_set_wrap input[name=name]");
            var name = name_target.val();

            var env_ids = [];
            $(".server_set_wrap select[name='env[]'] option:selected").each(function () {
                env_ids.push( $(this).val() );
            });


            if( !common_ops.validate.length( name,1,15 )) {
                common_ops.tip("请输入符合规范的名称~~", name_target);
                return;
            }

            if( env_ids.length < 1  ){
                common_ops.alert("请选择支持环境~~");
                return;
            }

            var data = $(".server_set_wrap form").serialize();
            btn_target.addClass("disabled");

            $.ajax({
                url: home_common_ops.buildUrl("/job/server/set"),
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
        });

    }
};

$(document).ready(function () {
    server_set_ops.init();
});
