import csv
from django.http import HttpResponse
from core.models import Task
from topic.models import Topic

def export_task_as_csv_action(description="Export selected objects as CSV file", fields=None, exclude=None, header=True):
    """
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

        
        field_names = ['user', 'topic_id', 'topic_question', 'left_doc', 'right_doc', 'action', 'created_at', 'completed_at']
        
        writer.writerow(list(field_names))

        for obj in queryset:
            action_dict = {1: "Right", 2: "Equal", 3: "Left"}
            task = Task.objects.get(id = obj.task_id)
            topic = Topic.objects.get(id = task.topic_id)
            action = action_dict[obj.action]
            
            writer.writerow([obj.user.username, topic.uuid, topic.title, obj.left_response.document.uuid, obj.right_response.document.uuid, action, obj.created_at, obj.completed_at])

        return response

    export_as_csv.short_description = description
    return export_as_csv