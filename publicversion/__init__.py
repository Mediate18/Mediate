def register(model, table_name=None):
    """
    Registers a model to have a 'public' equivalent.
    """

    # Create a public model
    # with a link to the base model
    # and other extra fields for administration purposes.
    # ForeignKeys in the public model refer to other public models.

    # Add a publish method to the base model
