from dal import autocomplete
from django.db.models import Q

from .models import User


class UserAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete View for user field
    """
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return User.objects.none()

        queryset = User.objects.filter(~Q(pk=self.request.user.pk))

        if self.q:
            queryset = queryset.filter(username__istartswith=self.q)

        return queryset
