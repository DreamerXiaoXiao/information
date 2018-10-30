function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    // 取消关注当前新闻作者
    $(".focused").click(function () {
        var user_id = $(this).attr('data-userid')
        var params = {
            "action": "unfollow",
            "user_id": user_id
        }
        $.ajax({
            url: "/news/user_followed",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    // window.location.reload();
                    location.href = '/user/user_follow?page=1'
                } else if (resp.errno == "4101") {
                    // 未登录，弹出登录框
                    $('.login_form_con').show();
                } else {
                    // 取消关注失败
                    alert(resp.errmsg)
                }
            }
        });
    });
});