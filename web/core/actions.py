import csv
from django.http import HttpResponse

def export_task_as_csv_action(description="Export selected objects as CSV file", fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
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

        
        field_names = ['ID', 'Topic', 'Is Completed', 'Grade', 'Document UUID']
        
        writer.writerow(list(field_names))
        
        for obj in queryset:
            best_answers = obj.best_answers.split('--')[1:]

            for i, ans in enumerate(best_answers):
                temp = ans.split("|")[:-1]
                if temp:
                    grade = f'{i+1}'
                for doc in temp:
                    writer.writerow([obj.id, obj.topic.title, obj.is_completed, grade, doc])

        return response

    export_as_csv.short_description = description
    return export_as_csv