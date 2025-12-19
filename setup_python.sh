# pyenv versions
pyenv install 3.13.5 
# pyenv install 3.11.9
pyenv virtualenv 3.13.5 .venv_bluenotebook
# pyenv virtualenv-delete .venv_bluenotebook
#pyenv virtualenv 3.11.9 .venv_bluenotebook
pyenv activate .venv_bluenotebook
# python -V
# pip -V
#xargs pip uninstall -y
# pip freeze > requirements.txt
pip install -r requirements.txt
# deactivate


# A chaque fois

bash
cd bluenotebook
pyenv activate .venv_bluenotebook
pip install -r requirements.txt
pip -V


```bash
$ git branch 				# check branches available
$  git checkout -b youtube-transcript-api 	# create and switch to youtube-transcript-api
$ vi xxx		# do some file modification
$ git add readme.txt			# stage file to the staging area
$ git status
$ git commit -m "updated readme"	# commit the file (experimental branch)
$ git status	
$ git branch			# still on experiment-branch
$ git checkout main		# back to the main branch
$ git branch			# set on main
$ git merge youtube-transcript-api	# Fast-Forward merge ok
$ git status			# nothing to commit
$ git log 			# check the commit
$ git push			# Push to remote repo
```

Pour memoire git checkout -b youtube-transcript-api 

  Voici la commande pour supprimer la branche experimental-branch :
```
$ git branch -D youtube-transcript-api  
```
Pour tester une pull request
# Récupère toutes les branches distantes
git fetch origin
# Liste les branches distantes pour vérifier le nom exact
git branch -r
# Ensuite checkout de la branche
git checkout -b nom-branche-local origin/nom-de-la-branche-distante


# pour mémoire
# pip install --upgrade pymupdf --> solve  "import" fitz error
=========== traduction Linux ===================

cd bluenotebook
pyenv activate .venv_bluenotebook
pylupdate5 -verbose  main.py gui/main_window.py -ts i18n/bluenotebook_en.ts
kate i18n/bluenotebook_en.ts  (change @default --> MainContext)
linguist i18n/bluenotebook_en.ts
lrelease i18n/bluenotebook_en.ts i18n/bluenotebook_en.qm
./run_bluenotebook.sh 


cd BlueNotebook
pyenv activate .venv_bluenotebook
cd bluenotebook/
./update_translations_pyqt5.sh 



*** ne pas oublier: pyenv activate .venv_bluenotebook *****

