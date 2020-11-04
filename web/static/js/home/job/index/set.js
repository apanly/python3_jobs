;

CONSTANT_FOREVER = 2 ;
var index_set_ops = {
    init: function () {
        this.eventBind();
        this.datetimeComponent();
    },
    eventBind: function () {
        var that = this;

        $(".index_set_wrap select[name='env_id']").change(function(){
            var selected_env_id = $(this).val();
            if( selected_env_id < 1 ){
                return;
            }
            $(".index_set_wrap select[name='server_id'] option").each(function(){
                if( $(this).val() < 1 ){
                    return true;
                }

                if( $(this).attr("data").indexOf( "-" + selected_env_id + "-" ) == -1 ){
                    $(this).attr("disabled","disabled");
                }else{
                    $(this).removeAttr("disabled");
                }

            });
        });
        $(".index_set_wrap select[name='env_id']").change();


        $(".index_set_wrap select[name=job_type]").change( function(){
            var target = $(".index_set_wrap input[name=run_interval]," +
                        ".index_set_wrap input[name=threshold_down]," +
                        ".index_set_wrap input[name=threshold_up]");
            if( $(this).val() == CONSTANT_FOREVER ){//常驻
                target.attr("readonly","readonly");
                target.parents(".form-group").hide();
            }else{
                target.removeAttr("readonly");
                target.parents(".form-group").show();
            }
        });
        $(".index_set_wrap select[name=job_type]").change();

        $(".index_set_wrap select[name='owner_uid'],.index_set_wrap select[name='relate_uid']").select2({
            language: "zh-CN",
            width: '100%'
        });

        $(".index_set_wrap .short_run_interval").click(function(){
            $(".index_set_wrap input[name=run_interval]").val( $(this).data()['min']);
        });

        $(".index_set_wrap .save").click(function () {
            var btn_target = $(this);
            if (btn_target.hasClass("disabled")) {
                common_ops.alert("正在保存，请不要重复提交~~");
                return false;
            }

            var cate_id_target = $(".index_set_wrap select[name=cate_id]");
            var cate_id = cate_id_target.val();

            var name_target = $(".index_set_wrap input[name=name]");
            var name = name_target.val();

            var env_id_target = $(".index_set_wrap select[name=env_id]");
            var env_id = env_id_target.val();

            var server_id_target = $(".index_set_wrap select[name=server_id]");
            var server_id = server_id_target.val();

            var owner_uid_target = $(".index_set_wrap select[name=owner_uid]");
            var owner_uid = owner_uid_target.val();

            var relate_uid_target = $(".index_set_wrap select[name=relate_uid]");
            var relate_uid = relate_uid_target.val();

            var command_target = $(".index_set_wrap input[name=command]");
            var command = command_target.val();

            var job_type_target = $(".index_set_wrap select[name=job_type]");
            var job_type = job_type_target.val();


            var next_run_time_target = $(".index_set_wrap input[name=next_run_time]");
            var next_run_time = next_run_time_target.val();

            var run_interval_target = $(".index_set_wrap input[name=run_interval]");
            var run_interval = run_interval_target.val();

            var threshold_down_target = $(".index_set_wrap input[name=threshold_down]");
            var threshold_down = threshold_down_target.val();

            var threshold_up_target = $(".index_set_wrap input[name=threshold_up]");
            var threshold_up = threshold_up_target.val();

            if( cate_id < 1 ){
                common_ops.tip("请选择分类~~", cate_id_target);
                return;
            }

            if( !common_ops.validate.length( name,1,15 )) {
                common_ops.tip("请输入符合规范的名称，长度不大于15个字符~~", name_target);
                return;
            }

            if( env_id < 1 ){
                common_ops.tip("请选择运行环境~~", env_id_target);
                return;
            }

            if( server_id < 1 ){
                common_ops.tip("请选择运行服务器~~", server_id_target);
                return;
            }

            if( owner_uid < 1 ){
                common_ops.tip("请选择Job负责人~~", owner_uid_target);
                return;
            }

            if( relate_uid < 1 ){
                common_ops.tip("请选择Job相关人~~", relate_uid_target);
                return;
            }

            if( !common_ops.validate.length( command,5 )) {
                common_ops.tip("请输入Job命令~~", command_target);
                return;
            }

            if( job_type < 1 ){
                common_ops.tip("请选择Job类型~~", job_type_target );
                return;
            }

            if( !common_ops.validate.date( next_run_time, /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/ )){
                common_ops.tip("请选择调度时间~~", next_run_time_target );
                return;
            }

            if( job_type != CONSTANT_FOREVER ) {
                if( run_interval == undefined || run_interval.length < 1 || parseInt( run_interval ) < 1 ){
                    common_ops.tip("请输入运行间隔~~", run_interval_target );
                    return;
                }

                if( threshold_down == undefined || threshold_down.length < 1 || parseInt( threshold_down ) < 0 ){
                    common_ops.tip("请输入预估最短运行时长~~", threshold_down_target );
                    return;
                }

                if( threshold_up == undefined || threshold_up.length < 1 || parseInt( threshold_up ) < 1 ){
                    common_ops.tip("请输入预估最长运行时长~~", threshold_up_target );
                    return;
                }
            }else{
                run_interval_target.val( 0 );
                threshold_down_target.val( 0 );
                threshold_up_target.val( 0 );
            }



            var data = $("form.index_set_wrap").serialize();
            btn_target.addClass("disabled");

            $.ajax({
                url: home_common_ops.buildUrl("/job/index/set"),
                data: data,
                type: 'POST',
                dataType: 'json',
                success: function (res) {
                    btn_target.removeClass("disabled");
                    var callback = {};
                    if (res.code == 200) {
                        callback = function () {
                            window.location.href = home_common_ops.buildUrl("/job/index/info",{ "id": res.data.id });
                        }
                    }
                    common_ops.msg(res.msg, res.code == 200, callback);
                }
            });
        });
    },
    datetimeComponent:function(){
        $.datetimepicker.setLocale('zh');
        params = {
            scrollInput: false,
            scrollMonth: false,
            scrollTime: false,
            timepicker: true,
            dayOfWeekStart: 1,
            lang: 'zh',
            todayButton: true,//回到今天
            defaultSelect: true,
            step: 5,
            format: 'Y-m-d H:i',//格式化显示
            onChangeDateTime: function (dp, $input) {}
        };
        $(".index_set_wrap input[name=next_run_time]").datetimepicker(params);
    }
};

$(document).ready(function () {
    index_set_ops.init();
});
