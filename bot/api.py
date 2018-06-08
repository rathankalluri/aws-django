# Custom object that we'll use to build our response.
class CustomResourceObject(object):
    def __init__(self, name=None, label=None):
        self.label = label
        self.name = name

# The Tastypie resource that will return our data.
# Make sure to inherit from Resource instead of ModelResource.
class CustomResource(Resource):
    # You will need to add fields for each property
    # that will be returned in the response.
    label = CharField(attribute='label', readonly=True)
    name = CharField(attribute='name', readonly=True)

    class Meta:
        # Start by disabling all routes for this resource
        allowed_methods = None
        # Allow the `get` index call where we will return data
        list_allowed_methods = ['get']
        # Use the custom object we created above
        object_class = CustomResourceObject
        # API endpoint for this resource
        resource_name = 'custom_endpoint'

    # Create our array of custom data
    def get_object_list(self, request):
        return map(lambda val: CustomResourceObject(label=val[0], name=val[1]), DjangoModel.CHOICES)

    # Return our custom data for the API call
    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)