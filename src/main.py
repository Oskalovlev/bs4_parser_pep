import re
import logging
from collections import defaultdict
from urllib.parse import urljoin

from requests import RequestException
import requests_cache
from tqdm import tqdm

from constants import (BASE_DIR, MAIN_DOC_URL, PEP_URL,
                       EXPECTED_STATUS, DOWNLOADS)
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import find_tag, cooking_soup
from exceptions import NotFoundException, ParserFindTagException


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = cooking_soup(session, whats_new_url)

    sections_by_python = soup.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    )

    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)

        soup = cooking_soup(session, version_link)

        h1, dl = (find_tag(soup, 'h1').text,
                  find_tag(soup, 'dl').text.replace('\n', ' '))
        result.append((version_link, h1, dl))
    return result


def latest_versions(session):
    soup = cooking_soup(session, MAIN_DOC_URL)

    sidebar = find_tag(
        soup, 'div', attrs={'class': 'sphinxsidebarwrapper'}
    )

    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise NotFoundException('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = cooking_soup(session, downloads_url)

    pdf_a4_link = soup.select_one(
        'table.docutils a[href$="pdf-a4.zip"]'
    )['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / DOWNLOADS
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    soup = cooking_soup(session, PEP_URL)

    tr_tags = soup.select('#numerical-index tbody tr')

    total_pep_count = 0
    status_pep_count = defaultdict(int)
    results = [('Status', 'Quantity')]

    for tr_tag in tqdm(tr_tags):

        td_tags = tr_tag.td

        all_status = None
        pep_link = None

        for pep_link in td_tags:
            pep_link = find_tag(
                td_tags.find_next_sibling('td'), 'a'
            ).get('href')
            pep_url = urljoin(PEP_URL, pep_link)
            soup = cooking_soup(session, pep_url)

            dl = find_tag(
                soup, 'dl', attrs={'class': 'rfc2822 field-list simple'}
            )

            pattern = (
                    r'.*(?P<status>Active|Draft|Final|Provisional|Rejected|'
                    r'Superseded|Withdrawn|Deferred|April Fool!|Accepted)'
                )
            re_text = re.search(pattern, dl.text)
            status = None
            if re_text:
                status = re_text.group('status')
            if all_status and EXPECTED_STATUS.get(all_status) != status:
                logging.info(
                    f'Несовпадающие статусы:\n{pep_url}\n'
                    f'Статус в карточке: {status}\n'
                    f'Ожидаемый статус: {EXPECTED_STATUS[all_status]}'
                )
            if not all_status and status not in ('Active', 'Draft'):
                logging.info(
                    f'Несовпадающие статусы:\n{pep_link}\n'
                    f'Статус в карточке: {status}\n'
                    f'Ожидаемые статусы: ["Active", "Draft"]'
                )
            total_pep_count += 1
            status_pep_count[status] += 1
    results.extend(
        [(status, status_pep_count[status]) for status in status_pep_count]
    )
    results.append(('Total', total_pep_count))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    try:
        configure_logging()
        logging.info('Парсер запущен!')

        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        logging.info(f'Аргументы командной строки: {args}')

        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()

        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)

        if results is not None:
            control_output(results, args)

        logging.info('Парсер завершил работу.')

    except (RequestException, ParserFindTagException) as error:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {error}',
            stack_info=True
        )


if __name__ == '__main__':
    main()
