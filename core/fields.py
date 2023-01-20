from django.db.models import signals, ImageField


class CustomImageField(ImageField):
    """Allows model instance to specify upload_to dynamically.

    Model class should have a method like:

        def get_upload_to(self, attname):
            return 'path/to/%d' % self.id

    Based on: http://code.djangoproject.com/wiki/CustomUploadAndFilters
    """
    def __init__(self, *args, **kwargs):
        if not 'upload_to' in kwargs:
            kwargs['upload_to'] = 'dummy'
        self.prime_upload = kwargs.get('prime_upload', False)
        if 'prime_upload' in kwargs:
            del(kwargs['prime_upload'])
        super(CustomImageField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        """Hook up events so we can access the instance."""
        super(CustomImageField, self).contribute_to_class(cls, name)
        if self.prime_upload:
            signals.post_init.connect(self._get_upload_to, sender=cls)
        signals.pre_save.connect(self._get_upload_to, sender=cls)

    def _get_upload_to(self, instance=None, **kwargs):
        """Get dynamic upload_to value from the model instance."""
        if hasattr(instance, 'get_upload_to'):
            self.upload_to = instance.get_upload_to(self.attname)

    def db_type(self, connection):
        """Required by Django for ORM."""
        return 'varchar(100)'
