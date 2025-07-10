from django_cron import cronScheduler, Job

from commits.models import Repository

class UpdateRepository(Job):
    run_every = 300

    def job(self):
        for repository in Repository.objects.all():
            repository.Update()
            print 'updated project: %s' % repository.name

cronScheduler.register(UpdateRepository)

