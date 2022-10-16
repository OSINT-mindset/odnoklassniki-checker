import asyncio
import logging
import requests
from json import JSONEncoder
from typing import List, Any

from aiohttp import TCPConnector, ClientSession

from .executor import AsyncioProgressbarQueueExecutor, AsyncioSimpleExecutor


OK_LOGIN_URL = \
    'https://www.ok.ru/dk?st.cmd=anonymMain&st.accRecovery=on&st.error=errors.password.wrong'
OK_RECOVER_URL = \
    'https://www.ok.ru/dk?st.cmd=anonymRecoveryAfterFailedLogin&st._aid=LeftColumn_Login_ForgotPassword'


class InputData:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class OutputData:
    def __init__(self, code, error, masked_name, masked_email,
                masked_phone, profile_info, profile_registred):
        self.code = code
        self.error = error
        self.masked_name = masked_name
        self.masked_email = masked_email
        self.masked_phone = masked_phone
        self.profile_info = profile_info
        self.profile_registred = profile_registred

    @property
    def fields(self):
        fields = list(self.__dict__.keys())
        fields.remove('error')

        return fields

    def __str__(self):
        error = ''
        if self.error:
            error = f' (error: {str(self.error)}'

        result = ''

        for field in self.fields:
            field_pretty_name = field.title().replace('_', ' ')
            value = self.__dict__.get(field)
            if value:
                result += f'{field_pretty_name}: {str(value)}\n'

        result += f'{error}'
        return result


class OutputDataList:
    def __init__(self, input_data: InputData, results: List[OutputData]):
        self.input_data = input_data
        self.results = results

    def __repr__(self):
        return f'Target {self.input_data}:\n' + '--------\n'.join(map(str, self.results))


class OutputDataListEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, OutputDataList):
            return {'input': o.input_data, 'output': o.results}
        elif isinstance(o, OutputData):
            return {k:o.__dict__[k] for k in o.fields}
        else:
            return o.__dict__


class Processor:
    def __init__(self, *args, **kwargs):
        from aiohttp_socks import ProxyConnector

        # make http client session
        proxy = kwargs.get('proxy')
        self.proxy = proxy
        if proxy:
            connector = ProxyConnector.from_url(proxy, ssl=False)
        else:
            connector = TCPConnector(ssl=False)

        self.session = ClientSession(
            connector=connector, trust_env=True
        )
        if kwargs.get('no_progressbar'):
            self.executor = AsyncioSimpleExecutor()
        else:
            self.executor = AsyncioProgressbarQueueExecutor()

        self.logger = logging.getLogger('processor')

    async def close(self):
        await self.session.close()


    async def request(self, input_data: InputData) -> OutputDataList:
        from bs4 import BeautifulSoup as bs
        status = 0
        error = None

        # odnoklassniki data
        masked_name = None
        masked_email = None
        masked_phone = None
        profile_info = None
        profile_registred = None

        try:
            login_data = input_data.value
            session = requests.Session()
            session.get(f'{OK_LOGIN_URL}&st.email={login_data}')
            request = session.get(OK_RECOVER_URL)
            status = request.status_code
            root_soup = bs(request.content, 'html.parser')
            soup = root_soup.find('div', {'data-l': 'registrationContainer,offer_contact_rest'})
            if soup:
                account_info = soup.find('div', {'class': 'ext-registration_tx taCenter'})
                masked_email = soup.find('button', {'data-l': 't,email'})
                masked_phone = soup.find('button', {'data-l': 't,phone'})
                if masked_phone:
                    masked_phone = masked_phone.find('div', {'class': 'ext-registration_stub_small_header'}).get_text()
                if masked_email:
                    masked_email = masked_email.find('div', {'class': 'ext-registration_stub_small_header'}).get_text()
                if account_info:
                    masked_name = account_info.find('div', {'class': 'ext-registration_username_header'})
                    if masked_name:
                        masked_name = masked_name.get_text()
                    account_info = account_info.findAll('div', {'class': 'lstp-t'})
                    if account_info:
                        profile_info = account_info[0].get_text()
                        profile_registred = account_info[1].get_text()

            if root_soup.find('div', {'data-l': 'registrationContainer,home_rest'}):
                output_data = None
            else:        
                output_data = OutputData(
                    status,
                    error,
                    masked_name=masked_name,
                    masked_email=masked_email,
                    masked_phone=masked_phone,
                    profile_info=profile_info,
                    profile_registred=profile_registred,
                )

        except Exception as e:
            error = e
            self.logger.error(e, exc_info=False)

        results = OutputDataList(input_data, [output_data] if output_data else [])

        return results


    async def process(self, input_data: List[InputData]) -> List[OutputDataList]:
        tasks = [
            (
                self.request, # func
                [i],          # args
                {}            # kwargs
            )
            for i in input_data
        ]

        results = await self.executor.run(tasks)

        return results
