import requests
import datetime


def get_authorization_header(request):
    """Returns a dict for Authorization token"""
    social = request.user.social_auth.get(provider='drchrono')
    access_token = social.extra_data['access_token']
    authorization = 'Bearer %s' % access_token
    return {'Authorization': authorization, }


def make_api_get_request(request, url, params=None):
    """Returns the data if successful, or none"""
    if not url:
        return None

    headers = get_authorization_header(request=request)
    response = requests.get(url=url, headers=headers, params=params)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        return None


def make_api_patch_request(request, url, data, params=None):
    """Returns True if successful, False otherwise"""
    if not data or not url:
        return False

    headers = get_authorization_header(request=request)
    response = requests.patch(url=url, headers=headers,
                              params=params, data=data)
    if response.status_code == requests.codes.no_content:
        return True
    else:
        return False


def get_patient_id(request, first_name, last_name):
    params = {'first_name': first_name,
              'last_name': last_name, }

    url = 'https://drchrono.com/api/patients_summary'
    data = make_api_get_request(request=request, url=url, params=params)

    if data:
        appointments = data['results']
        if appointments[0]['id']:
            return appointments[0]['id']

    return None


def get_appointment_id(request, patient_id):
    date_today = datetime.date.today().isoformat()
    params = {'date': date_today,
              'patient': patient_id, }

    url = 'https://drchrono.com/api/appointments'
    data = make_api_get_request(request=request, url=url, params=params)

    if data:
        appointments = data['results']

        for appointment in appointments:
            if str(appointment['patient']) == patient_id:
                return appointment['id']
    return None


def get_patient_info(request, patient_id):

    url = 'https://drchrono.com/api/patients/' + str(patient_id)
    data = make_api_get_request(request=request, url=url)
    if data:
        return data

    return None


def update_arrived(request, appointment_id):

    data = {'status': 'Arrived', }

    url = 'https://drchrono.com/api/appointments/' + appointment_id
    response = make_api_patch_request(request=request, url=url, data=data)
    if response:
        return True
    else:
        return False


def update_demographic(request, patient_id, form):

    data = {'email': form['email'],
            'gender': form['gender'], }

    url = 'https://drchrono.com/api/patients/' + str(patient_id)
    try:
        response = make_api_patch_request(request=request, url=url, data=data)
    except DoesNotExist:
        return False

    return response


def check_doctor_id(request, doctor_id):
    url = 'https://drchrono.com/api/users/current'
    data = make_api_get_request(request=request, url=url)
    if data:
        if str(data['doctor']) == doctor_id:
            return True
    return False


def today_appointment_list(request):
    date_today = datetime.date.today().isoformat()

    # TODO: must disable auto suggestions
    params = {'date': date_today, }

    url = 'https://drchrono.com/api/appointments'
    try:
        data = make_api_get_request(request=request, url=url, params=params)
    except DoesNotExist:
        return None
    return data['results']


def get_patient_summary(request, patient_id):

    url = 'https://drchrono.com/api/patients_summary/' + str(patient_id)
    try:
        data = make_api_get_request(request=request, url=url)
    except DoesNotExist:
        return None
    return data
