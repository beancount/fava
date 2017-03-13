"""JSON API."""

import os

from flask import abort, Blueprint, jsonify, g, request
from werkzeug.utils import secure_filename
from beancount.core.data import Posting, Transaction
from beancount.core.amount import Amount
from beancount.core.number import D
from beancount.scripts.format import align_beancount

from fava import util
from fava.core.helpers import FavaAPIException


json_api = Blueprint('json_api', __name__)  # pylint: disable=invalid-name


def _api_error(message=''):
    return jsonify({'success': False, 'error': message})


def _api_success(**kwargs):
    kwargs['success'] = True
    return jsonify(kwargs)


@json_api.errorhandler(FavaAPIException)
def _json_api_exception(error):
    return _api_error(error.message)


@json_api.route('/changed/')
def changed():
    """Check for file changes."""
    return jsonify({'success': True, 'changed': g.ledger.changed()})


@json_api.route('/source/', methods=['GET', 'PUT'])
def source():
    """Read/write one of the source files."""
    if request.method == 'GET':
        data = g.ledger.file.get_source(request.args.get('file_path'))
        return _api_success(payload=data)
    elif request.method == 'PUT':
        if request.get_json() is None:
            abort(400)
        g.ledger.file.set_source(request.get_json()['file_path'],
                                 request.get_json()['source'])
        return _api_success()


@json_api.route('/format-source/', methods=['POST'])
def format_source():
    """Format beancount file."""
    if request.get_json() is None:
        abort(400)
    return _api_success(payload=align_beancount(request.get_json()['source']))


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

    file = request.files['file']
    if not file:
        raise FavaAPIException('No file uploaded.')

    documents_folder = request.form['folder']
    if documents_folder not in g.ledger.options['documents']:
        raise FavaAPIException('Not a documents folder: {}.'
                               .format(documents_folder))

    filepath = os.path.normpath(os.path.join(
        os.path.dirname(g.ledger.beancount_file_path),
        documents_folder,
        request.form['account'].replace(':', '/'),
        secure_filename(request.form['filename']).replace('_', ' ')))

    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    if os.path.isfile(filepath):
        raise FavaAPIException('{} already exists.'.format(filepath))

    file.save(filepath)

    if request.form.get('entry_hash'):
        g.ledger.file.insert_metadata(request.form['entry_hash'],
                                      'statement',
                                      os.path.basename(filepath))
    return _api_success(message='Uploaded to {}'.format(filepath))


@json_api.route('/add-transaction/', methods=['PUT'])
def add_transaction():
    """Add a transaction."""
    json = request.get_json()

    postings = []
    for posting in json['postings']:
        if posting['account'] not in g.ledger.attributes.accounts:
            return _api_error('Unknown account: {}.'
                              .format(posting['account']))
        number = D(posting['number']) if posting['number'] else None
        amount = Amount(number, posting.get('currency'))
        postings.append(Posting(posting['account'], amount,
                                None, None, None, None))

    if not postings:
        return _api_error('Transaction contains no postings.')

    date = util.date.parse_date(json['date'])[0]
    transaction = Transaction(
        json['metadata'], date, json['flag'], json['payee'],
        json['narration'], None, None, postings)

    g.ledger.file.insert_transaction(transaction)
    return _api_success(message='Stored transaction.')
