import requests


def _create_subject(cookies, url, project, subject, group, weight, height, gender, yob, age, handedness):
    subject_url = '{}/REST/projects/{}/subjects/{}'.format(
        url, project, subject
    )
    sep = '?'

    params = [
        ('group', group),
        ('weight', weight),
        ('height', height),
        ('gender', gender),
        ('yob', yob),
        ('age', age),
        ('handedness', handedness)
    ]

    for key, val in params:
        if val is not None:
            subject_url = '{}{}{}={}'.format(
                subject_url, sep, key, val
            )
            sep = '&'

    r = requests.put(
        subject_url,
        cookies=cookies
    )
    r.raise_for_status()


def _create_experiment(cookies, url, project, subject, experiment, xsi_type):
    experiment_url = '{}/REST/projects/{}/subjects/{}/experiments/{}?xsiType={}'.format(
        url, project, subject, experiment, xsi_type
    )
    r = requests.put(
        experiment_url,
        cookies=cookies
    )
    r.raise_for_status()


def _create_container_and_upload_file(
    cookies,
    url,
    local_path,
    project,
    subject,
    experiment,
    container_type,
    xsi_type,
    container,
    file_name,
    resource
):
    resource = resource if resource is not None else 'OTHER'
    overwrite_existing_file = True
    verify = True

    r = requests.get(
        '{}/REST/projects/{}/subjects/{}/experiments/{}/{}?format=json'.format(
            url, project, subject, experiment, container_type
        ),
        cookies=cookies,
        verify=verify
    )
    r.raise_for_status()
    existing_containers = r.json()['ResultSet']['Result']

    container_exists = False
    existing_xsi_type = None

    for ec in existing_containers:
        if ('ID' in ec and ec['ID'] == container) or ('label' in ec and ec['label'] == container):
            container_exists = True
            existing_xsi_type = ec['xsiType']
            break

    if not container_exists:
        # create container
        container_url = '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}'.format(
            url, project, subject, experiment, container_type, container
        )

        if xsi_type:
            container_url = '{}?xsiType={}'.format(container_url, xsi_type)

        r = requests.put(
            container_url,
            cookies=cookies,
            verify=verify
        )
        r.raise_for_status()

        # create file
        with open(local_path, 'rb') as f:
            r = requests.put(
                '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files/{}?inbody=true'.format(
                    url, project, subject, experiment, container_type, container, resource, file_name
                ),
                data=f,
                cookies=cookies,
                verify=verify
            )
            r.raise_for_status()

    else:
        if xsi_type and xsi_type != existing_xsi_type:
            raise Exception(
                'xsi_type "{}" of existing container "{}" does not match provided xsi_type "{}"'.format(
                    existing_xsi_type, container, xsi_type))

        r = requests.get(
            '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources?format=json'.format(
                url, project, subject, experiment, container_type, container
            ),
            cookies=cookies,
            verify=verify
        )
        r.raise_for_status()
        existing_resources = r.json()['ResultSet']['Result']

        resource_exists = False
        for er in existing_resources:
            if ('ID' in er and er['ID'] == resource) or ('label' in er and er['label'] == resource):
                resource_exists = True
                break

        if not resource_exists:
            # create file
            with open(local_path, 'rb') as f:
                r = requests.put(
                    '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files/{}?inbody=true'.format(
                        url, project, subject, experiment, container_type, container, resource, file_name
                    ),
                    data=f,
                    cookies=cookies,
                    verify=verify
                )
                r.raise_for_status()

        else:
            r = requests.get(
                '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files?format=json'.format(
                    url, project, subject, experiment, container_type, container, resource
                ),
                cookies=cookies,
                verify=verify
            )
            r.raise_for_status()
            existing_files = r.json()['ResultSet']['Result']

            file_exists = False
            for ef in existing_files:
                if 'Name' in ef and ef['Name'] == file_name:
                    file_exists = True
                    break

            if file_exists:
                if not overwrite_existing_file:
                    raise Exception(
                        'File "{}" already exists and overwrite_existing_file is not set.'.format(file_name)
                    )
                # delete file
                r = requests.delete(
                    '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files/{}'.format(
                        url, project, subject, experiment, container_type, container, resource, file_name
                    ),
                    cookies=cookies,
                    verify=verify
                )
                r.raise_for_status()

            # create file
            with open(local_path, 'rb') as f:
                r = requests.put(
                    '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files/{}?inbody=true'.format(
                        url, project, subject, experiment, container_type, container, resource, file_name
                    ),
                    data=f,
                    cookies=cookies,
                    verify=verify
                )
                r.raise_for_status()
