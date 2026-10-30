# 本地提取与来源核对

输入只读，输出独立目录。不能因同文件名或同basename自动去重；先确认每份资料的实际内容与版本。

DOCX按XML顺序保留正文、内容控件、表格及页眉页脚、脚注尾注出处；合并格保留锚点而不重复金额。正文图片导出给当前agent看；不确定修订登记待办。Word没有固定物理页码，不能由段落序号猜页。
PDF逐页读取文字与表格，保留实际物理页码；图片/空页登记待核实，不能仅凭表格外文字少判缺页。
XLSX/XLSM同时检查公式和缓存；无缓存保留空值和待办，不零补、不自动重算保存源文件。
PNG/JPEG等登记原图给当前agent视觉；旧DOC或不可读来源保留未执行并说明需要可读版本。脚本不能声称看过图片。

产物：report.md全文及来源标记；extracted_tables.json含schema_version=2、source_root、sources、files、tables、segments、pending；files_index.json含原路径/读取方式/SHA-256。
tables使用row_model=all_raw、headers=[]，rows[0]是原始第0行，可能为表头；id是提取内全局表ID。page/chapter/sheet只保留真实可得位置。索引从0开始，不是印刷页码。

当前agent逐项核对首末页、段落、表数量、续表、第一行、合并格、单位、两期、合并/母公司、签章和识别缺口。补充提取后重新初始化；旧指纹结论不得当成已完成。

精确取数用source及table_id/sheet、first_data_row、last_data_row（不含末端）、item_col/current_col/prior_col。重名冲突报错，不取最后值；原值/余额/净值不是别名。复杂表头先还原层次再定公式。空白/横线不自动零；当前agent确认横线确为零后可在验算表设dash_is_zero=true。单位声明与金额内嵌单位冲突报错。

Word正文和单元格保留制表符、换行及段落分隔；不能把多行披露拼成一个数字。文件夹输入先完整登记实际文件，不支持的xls等进入来源和未执行清单；不自动安装解析库。可选OCR失败仅登记补充失败，保留已完成的本地正文和表格。
