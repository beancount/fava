"""JSON API."""

import os

from flask import Blueprint, jsonify, g, request
from werkzeug.utils import secure_filename
from beancount.core import data
from beancount.core.amount import Amount
from beancount.core.number import D
from beancount.scripts.format import align_beancount

from fava import util
from fava.core.file import save_entry_slice
from fava.core.helpers import FavaAPIException
from fava.core.misc import extract_tags_links

json_api = Blueprint('json_api', __name__)  # pylint: disable=invalid-name


def _api_success(**kwargs):
    kwargs['success'] = True
    return jsonify(kwargs)


@json_api.errorhandler(FavaAPIException)
def _json_api_exception(error):
    return jsonify({'success': False, 'error': error.message})


@json_api.errorhandler(OSError)
def _json_api_oserror(error):
    return jsonify({'success': False, 'error': error.strerror})


@json_api.route('/changed/')
def changed():
    """Check for file changes."""
    return jsonify({'success': True, 'changed': g.ledger.changed()})


@json_api.route('/errors/')
def errors():
    """Number of errors."""
    return jsonify({'success': True, 'errors': len(g.ledger.errors)})


@json_api.route('/source/', methods=['PUT'])
def source():
    """Read/write one of the source files."""
    request_data = request.get_json()
    if request_data is None:
        raise FavaAPIException('Invalid JSON request.')
    if request_data.get('file_path'):
        sha256sum = g.ledger.file.set_source(
            request_data.get('file_path'),
            request_data.get('source'), request_data.get('sha256sum'))
    else:
        entry = g.ledger.get_entry(request_data.get('entry_hash'))
        sha256sum = save_entry_slice(entry,
                                     request_data.get('source'),
                                     request_data.get('sha256sum'))
    return _api_success(sha256sum=sha256sum)


@json_api.route('/format-source/', methods=['POST'])
def format_source():
    """Format beancount file."""
    request_data = request.get_json()
    if request_data is None:
        raise FavaAPIException('Invalid JSON request.')
    return _api_success(payload=align_beancount(request_data['source']))


@json_api.route('/payee-accounts/', methods=['GET'])
def payee_accounts():
    """Rank accounts for the given payee."""
    return _api_success(
        payload=g.ledger.attributes.payee_accounts(request.args.get('payee')))


@json_api.route('/add-document/', methods=['PUT'])
def add_document():
    """Upload a document."""
    if not g.ledger.options['documents']:
        raise FavaAPIException('You need to set a documents folder.')

    upload = request.files['file']
    if not upload:
        raise FavaAPIException('No file uploaded.')

    documents_folder = request.form['folder']
    if documents_folder not in g.ledger.options['documents']:
        raise FavaAPIException('Not a documents folder: {}.'
                               .format(documents_folder))

    filename = upload.filename
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')

    if not os.path.supports_unicode_filenames:
        filename = secure_filename(filename)

    directory = os.path.normpath(
        os.path.join(
            os.path.dirname(g.ledger.beancount_file_path), documents_folder,
            *request.form['account'].split(':')
        ))
    filepath = os.path.join(directory, filename)

    if os.path.exists(filepath):
        raise FavaAPIException('{} already exists.'.format(filepath))

    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    upload.save(filepath)

    if request.form.get('entry_hash'):
        g.ledger.file.insert_metadata(request.form['entry_hash'], 'statement',
                                      filename)
    return _api_success(message='Uploaded to {}'.format(filepath))


def json_to_entry(json_entry, valid_accounts):
    """Parse JSON to a Beancount entry."""
    # pylint: disable=not-callable
    date = util.date.parse_date(json_entry['date'])[0]
    if json_entry['type'] == 'transaction':
        narration, tags, links = extract_tags_links(json_entry['narration'])
        txn = data.Transaction(json_entry['metadata'], date,
                               json_entry['flag'], json_entry['payee'],
                               narration, tags, links, [])

        if not json_entry.get('postings'):
            raise FavaAPIException('Transaction contains no postings.')

        for posting in json_entry['postings']:
            if posting['account'] not in valid_accounts:
                raise FavaAPIException('Unknown account: {}.'
                                       .format(posting['account']))
            data.create_simple_posting(txn, posting['account'],
                                       posting.get('number') or None,
                                       posting.get('currency'))

        return txn
    elif json_entry['type'] == 'balance':
        if json_entry['account'] not in valid_accounts:
            raise FavaAPIException(
                'Unknown account: {}.'.format(json_entry['account']))
        number = D(json_entry['number'])
        amount = Amount(number, json_entry.get('currency'))

        return data.Balance(json_entry['metadata'], date,
                            json_entry['account'], amount, None, None)
    elif json_entry['type'] == 'note':
        if json_entry['account'] not in valid_accounts:
            raise FavaAPIException(
                'Unknown account: {}.'.format(json_entry['account']))

        if '"' in json_entry['comment']:
            raise FavaAPIException('Note contains double-quotes (")')

        return data.Note(json_entry['metadata'], date, json_entry['account'],
                         json_entry['comment'])
    else:
        raise FavaAPIException('Unsupported entry type.')


@json_api.route('/add-entries/', methods=['PUT'])
def add_entries():
    """Add multiple entries."""
    request_data = request.get_json()
    if request_data is None:
        raise FavaAPIException('Invalid JSON request.')

    try:
        entries = [
            json_to_entry(entry, g.ledger.attributes.accounts)
            for entry in request_data['entries']
        ]
    except KeyError as error:
        raise FavaAPIException('KeyError: {}'.format(str(error)))

    g.ledger.file.insert_entries(entries)

    return _api_success(message='Stored {} entries.'.format(len(entries)))
