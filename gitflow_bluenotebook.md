# BlueNotebook Gitflow

based on 🔖 [Bookmark | A successful Git branching model » nvie.com - https://nvie.com/posts/a-successful-git-branching-model/](https://nvie.com/posts/a-successful-git-branching-model/)

Simple git workflow

- `main` branch (Changes must be made through a pull request PR). Support Releases and tags
- `develop` branch can be seen as integration branch for new features  and Fixes branches

- `feature` branches used to implement new code to be merge to `develop`

- `hotfix` branches  used to correct majors  blocking bugs to be merge directly  to `main` using Pull Request PR

We used `--no-ff` flag merge. The `--no-ff` flag causes the merge to always create a new commit object, even if the merge could be performed with a fast-forward. This avoids losing information about the historical existence of a feature branch and groups together all commits that together added the feature. 

## Create develope branch (1 time)

```bash
$ git checkout -b develop master (done @Github)
..
git push --set-upstream origin develop
```


## Creating a feature branch

```bash
$ git switch develop
$ git pull
$ git checkout -b vX.Y.Z_feature develop
Switched to a new branch "vX.Y.Z_feature"
...
do work
....
$ git add .
$ git commit -a -m "zerzerzerze"

do work
....
$ git add .
$ git commit -a -m "zerzerzerze"
```

## Incorporating a finished feature on develop

```bash
$ git checkout develop
Switched to branch 'develop'
$ git merge --no-ff vX.Y.Z_feature
Updating ea1b82a..05e9557
(Summary of changes)
$ git branch -d vX.Y.Z_feature
Deleted branch vX.Y.Z_feature (was 05e9557).
$ git push origin develop
```

## Finishing a release branch (merge develop --> Main using PR)

```bash
$ git checkout main
Switched to branch 'main'
$ git push
Everything up-to-date
$ git merge --no-ff develop
Updating ea1b82a..05e9557
(Summary of changes)
$ git merge --no-ff release-1.2
Merge made by the 'ort' strategy.
(Summary of changes)
```
##  ------ Push to main should be done using a pull request PR -----------------------
```bash
$ git push
Énumération des objets: 1, fait.
Décompte des objets: 100% (1/1), fait.
Écriture des objets: 100% (1/1), 226 octets | 226.00 Kio/s, fait.
Total 1 (delta 0), réutilisés 0 (delta 0), réutilisés du paquet 0 (depuis 0)
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote: Review all repository rules at https://github.com/lephotographelibre/BlueNotebook/rules?ref=refs%2Fheads%2Fmain
remote:
remote: - Changes must be made through a pull request.
```

## -- Open a PR on Gthub in order to be able to merge develop and main (After approvalthe merge isn't done on Github !! ) -------------
```bash
$ git pull origin develop
$ git pull origin main
$ git checkout main
$ git merge --no-ff  develop
$ git push -u origin main
$ git pull
Déjà à jour.
```
## Creating the hotfix branch

Hotfix branches are created from the main branch.
For example, say version 1.2 is the current production
release running live and causing troubles due to a
severe bug. But changes on develop are yet
unstable. We may then branch off a hotfix branch and
start fixing the problem:

```bash
$ git checkout -b hotfix-1.2.1 main
Switched to a new branch "hotfix-1.2.1"

Then, fix the bug and commit the fix in one or more separate commits.
```bash
$ git commit -m "Fixed severe production problem"
[hotfix-1.2.1 abbe5d6] Fixed severe production problem
5 files changed, 32 insertions(+), 17 deletions(-)
```

## Finishing a hotfix branch Open a PR on Gthub in order to be able to merge develop and main (After approvalthe merge isn't done on Github !! ) 
When finished, the bugfix needs to be merged back into main , but also needs to be merged back
into develop , in order to safeguard that the bugfix is included in the next release as well. This is
completely similar to how release branches are finished.
First, update master and tag the release.

```bash
$ git checkout main  #-->  Open a PR on Gthub in order to be able to merge develop and main (After approvalthe merge isn't done on Github !! ) 
Switched to branch 'main'
# After approval the merge isn't done on Github !! 
$ git merge --no-ff hotfix-1.2.1
Merge made by recursive.
(Summary of changes)
$ git tag -a v1.2.1 -m "Release 1.2.1"
$ git push origin main
$ git push origin v1.2.1
```

Next, include the bugfix in develop , too:

```bash
$ git checkout develop
Switched to branch 'develop'
$ git merge --no-ff hotfix-1.2.1
Merge made by recursive.
(Summary of changes)
$ git push origin develop
```

Finally, remove the temporary branch:
```bash
$ git branch -d hotfix-1.2.1
Deleted branch hotfix-1.2.1 (was abbe5d6).
```
