*** Settings ***
Documentation     登录it.yusys.com.cn
resource          yusys_resource.robot
Suite Setup       打开网页    ${登录页}
# Suite Teardown    退出

*** Variables ***


*** Test Cases ***
登录
    Title Should Start With    资源管理
    Input Text       identifier:loginname   ${用户名}
    Input Text       identifier:password    ${密码}
    ${checkcode}=    Get Value From User    输入验证码        default_value=
    Input Text       identifier:checkcode   ${checkcode}
    Click Button     login_btn
    Wait Until Element Is Enabled   css:#research-system       60


