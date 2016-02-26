def get_version(version=None):
    """Returns a tuple of the django version. If version argument is non-empty,
    then checks for correctness of the tuple provided.
    """

    if version[4] > 0:  # 0.2.1-alpha.1
        return "{}.{}.{}-{}.{}".format(version[0], version[1], version[2], version[3], version[4])
    elif version[3] != '':  # 0.2.1-alpha
        return "{}.{}.{}-{}".format(version[0], version[1], version[2], version[3])
    elif version[2] > 0:  # 0.2.1
        return "{}.{}.{}".format(version[0], version[1], version[2])
    else:  # 0.2
        return "{}.{}".format(version[0], version[1])
