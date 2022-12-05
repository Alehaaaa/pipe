class Permissions(object):


    #[adminstrator]
    edit_project_settings = 0
    delete_branch = 0
    create_branch = 0
    rename = 0

    #[superviser]
    delete = 1
    create_category = 1
    create_component = 1
    create_preset = 1

    #[lead]
    delete_master = 2
    revert_master = 2
    import_version = 2

    #[junior]
    save_version = 3
    save_playblast = 3
    save_master = 3
    delete_playblast = 3
    delete_version = 3

    #[watch]
    reference_version = 4
    n_a = 4


    roles = {'administrator': 0,
             'supervisor' : 1,
             'lead' : 2,
             'junior' : 3,
             'view': 4}

    @classmethod
    def role_int(cls, role_strig):
        try:
            return cls.roles[role_strig]
        except:
            return 0

    @classmethod
    def has_permissions(cls, role_string, action ):

        if cls.role_int(role_string)  > action:
            return False

        return True


