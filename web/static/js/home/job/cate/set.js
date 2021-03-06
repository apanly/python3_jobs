;
var cate_set_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        var that = this;
        $(".cate_set_wrap .save").click(function () {
            var btn_target = $(this);
            if (btn_target.hasClass("disabled")) {
                common_ops.alert("正在保存，请不要重复提交~~");
                return false;
            }

            var name_target = $(".cate_set_wrap input[name=name]");
            var name = name_target.val();

            if( !common_ops.validate.length( name,1,15 )) {
                common_ops.tip("请输入符合规范的名称~~", name_target);
                return;
            }


            var data = $(".cate_set_wrap form").serialize();
            btn_target.addClass("disabled");

            $.ajax({
                url: home_common_ops.buildUrl("/job/cate/set"),
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
    cate_set_ops.init();
});
