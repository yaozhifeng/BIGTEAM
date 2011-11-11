from django.db import models
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist
import datetime
from svnclient.svnlogclient import SVNLogClient
from svnclient.svnlogiter import SVNRevLogIter

BINARYFILEXT = [ 'doc', 'xls', 'ppt', 'docx', 'xlsx', 'pptx', 'dot', 'dotx', 'ods', 'odm', 'odt', 'ott', 'pdf',
                 'o', 'a', 'obj', 'lib', 'dll', 'so', 'exe',
                 'jar', 'zip', 'z', 'gz', 'tar', 'rar','7z',
                 'pdb', 'idb', 'ilk', 'bsc', 'ncb', 'sbr', 'pch', 'ilk',
                 'bmp', 'dib', 'jpg', 'jpeg', 'png', 'gif', 'ico', 'pcd', 'wmf', 'emf', 'xcf', 'tiff', 'xpm',
                 'gho', 'mp3', 'wma', 'wmv','wav','avi'
                 ]


# Create your models here.

class Repository(models.Model):
    name = models.CharField('name', max_length=50)
    desc = models.CharField('description', max_length=250)
    url = models.CharField('repository url', max_length=500)
    username = models.CharField('username', max_length=50)
    password = models.CharField('password', max_length=50)

    def __unicode__(self):
        return self.name

    def clear(self):
        CommitLog.objects.filter(repository=self).delete()

    def update(self):
        svnclient = SVNLogClient(self.url, username=self.username, password=self.password)
        try:
            laststoredrev = self.getLastStoredRev()
            rootUrl = svnclient.getRootUrl()
            (startrev, endrev) = svnclient.findStartEndRev(None, None)
            startrev = max(startrev, laststoredrev+1)

            if startrev <= endrev:
                self.convert(svnclient, startrev, endrev)

            self.save()
        except Exception as e:
            print 'Exception updating project'
            print e

    def convert(self, svnclient, startrev, endrev):
        svnloglist = SVNRevLogIter(svnclient, startrev, endrev)

        for rev in svnloglist:
            if rev.isvalid():
                try:
                    log = CommitLog(repository = self,
                        revision = rev.revno,
                        time = rev.date,
                        author = self.addAuthor(rev.author),
                        comment = rev.message)
                    log.save()
                    print 'converted revision %d' % rev.revno
                except Exception as e:
                    print 'exception converting revision %d' % rev.revno
                    print e

    def addAuthor(self, account):
        try:
            author = Author.objects.get(account=account)
        except ObjectDoesNotExist:
            author = Author(account=account)
            author.save()
        return author

    def getLastStoredRev(self):
        try:
            last = self.commits.aggregate(maxrev = Max('revision'))
            rev = last['maxrev']
            if rev is None:
                rev = 0
            return rev
        except:
            return 0

class Author(models.Model):
    account = models.CharField('name', max_length=50)
    display = models.CharField('display name', max_length=50)

    def __unicode__(self):
        return self.account

class CommitLog(models.Model):
    repository = models.ForeignKey(Repository, related_name='commits')
    revision = models.IntegerField('revision number')
    time = models.DateTimeField('commit time')
    author = models.ForeignKey(Author, related_name='commits')
    comment = models.TextField('commit comment')

    def __unicode__(self):
        return 'r%d' % self.revision


