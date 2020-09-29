# # 每次推送检查仓库.git文件夹大小，需要定期在远程仓库gc
sizes=(`du -d0 .git`)
if [ ${sizes[0]} -gt 800000 ]
then
# 注意，此操作会造成所有提交历史log完全删除，不可恢复，建议提前备份
	git checkout --orphan latest_branch  # 新建空分支
	mongodump -d leanote -o leanote_db
	cp -r /home/nvidia/projects ./
	git add -A -v >> git.log
	git commit -m "update`date`"
	git branch -D master
	git branch -m master
	git push -f origin master >> git.log
	date >> git.log
	git branch --set-upstream-to=origin/master
else
	# 大小较小使用常规增量更新，提高效率
	mongodump -d leanote -o leanote_db
	cp -r /home/nvidia/projects ./
	git add . -v >> git.log
	git commit -m "update"
	git push >> git.log
	date >> git.log
fi
