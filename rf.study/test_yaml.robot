*** Settings ***
Documentation     测试yaml变量文件，dict中包括list
...               作为配置信息
Library           Collections
Library           String
Variables         variables_dict.yaml

*** Variables ***
@{月份}     201806      201807
${名称}     部门损益明细表【项目】-完工百分比法
@{口径}     考核口径     管理口径
${workdir}  X:/Temp

&{scope}         BOTTOM=1   LEFT=1   RIGHT=0   TOP=3
&{col1}          COL=1    COL_NAME=月份    CONTENT=${月份[0]}
&{col35}         COL=35   COL_NAME=口径    CONTENT=${口径[0]}
@{cols}          &{col1}    &{col35}
&{add_cols}      cols=@{cols}
${sheetname}     项目-${口径[0]}
${源文件}         ${workdir}/${月份[0]}/${名称}-${口径[0]}-${月份[0]}.xls
${目标文件}       ${workdir}/部门损益明细表-整理后-${月份[0]}.xls
&{request}       scope=&{scope}    add_cols=&{add_cols}    sheetname=${sheetname}    源文件=${源文件}    目标文件=${目标文件}


*** Test Cases ***
验证yaml文件
    Log Variables
    Log Many     ${xmsymx}       
    Log Many     ${fxmsymx}       
    Log Many     ${xmrymx}       
    Log Many     ${request}       
    Log Many     ${workdir}       
    Log Many     ${request.scope.TOP}       
    Log Many     ${request.add_cols}