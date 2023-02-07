import csv
from django.http import HttpResponse


def export_task_as_csv_action(description="Export selected objects as CSV file", fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    """
    def export_as_csv(modeladmin, request, queryset):
        """
        """
        opts = modeladmin.model._meta
        field_names = set([field.name for field in opts.fields])

        if fields:
            fieldset = set(fields)
            field_names = field_names & fieldset

        elif exclude:
            excludeset = set(exclude)
            field_names = field_names - excludeset

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % str(opts).replace('.', '_')

        writer = csv.writer(response)

        
        field_names = ['ID', 'Username', 'Topic ID', 'Is Completed', 'Grade', 'Document UUID']
        
        writer.writerow(list(field_names))
        
        for obj in queryset:
            best_answers = obj.best_answers.split('--')[1:]

            for i, ans in enumerate(best_answers):
                temp = ans.split("|")[:-1]
                if temp:
                    grade = f'{i+1}'
                for doc in temp:
                    writer.writerow([obj.id, obj.user.username, obj.topic.uuid, obj.is_completed, grade, doc])

        return response

    export_as_csv.short_description = description
    return export_as_csv