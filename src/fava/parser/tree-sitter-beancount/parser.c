#include <tree_sitter/parser.h>

#if defined(__GNUC__) || defined(__clang__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#endif

#define LANGUAGE_VERSION 11
#define STATE_COUNT 267
#define LARGE_STATE_COUNT 2
#define SYMBOL_COUNT 99
#define ALIAS_COUNT 0
#define TOKEN_COUNT 49
#define EXTERNAL_TOKEN_COUNT 0
#define FIELD_COUNT 27
#define MAX_ALIAS_SEQUENCE_LENGTH 7

enum {
  aux_sym__skipped_lines_token1 = 1,
  aux_sym__skipped_lines_token2 = 2,
  anon_sym_COLON = 3,
  aux_sym__skipped_lines_token3 = 4,
  aux_sym_metadata_token1 = 5,
  anon_sym_include = 6,
  anon_sym_option = 7,
  anon_sym_plugin = 8,
  anon_sym_pushtag = 9,
  anon_sym_poptag = 10,
  anon_sym_pushmeta = 11,
  anon_sym_popmeta = 12,
  anon_sym_LBRACE = 13,
  anon_sym_RBRACE = 14,
  anon_sym_LBRACE_LBRACE = 15,
  anon_sym_RBRACE_RBRACE = 16,
  anon_sym_COMMA = 17,
  anon_sym_STAR = 18,
  anon_sym_POUND = 19,
  anon_sym_AT_AT = 20,
  anon_sym_AT = 21,
  anon_sym_balance = 22,
  anon_sym_close = 23,
  anon_sym_commodity = 24,
  anon_sym_custom = 25,
  anon_sym_document = 26,
  anon_sym_event = 27,
  anon_sym_note = 28,
  anon_sym_open = 29,
  anon_sym_pad = 30,
  anon_sym_price = 31,
  anon_sym_query = 32,
  anon_sym_TILDE = 33,
  anon_sym_LPAREN = 34,
  anon_sym_RPAREN = 35,
  anon_sym_DASH = 36,
  anon_sym_PLUS = 37,
  anon_sym_SLASH = 38,
  sym_bool = 39,
  sym_date = 40,
  sym_key = 41,
  sym_tag = 42,
  sym_link = 43,
  sym_string = 44,
  sym_currency = 45,
  sym_number = 46,
  sym_flag = 47,
  sym_account = 48,
  sym_beancount_file = 49,
  sym__skipped_lines = 50,
  sym__key_value_value = 51,
  sym_key_value = 52,
  sym_metadata = 53,
  sym__undated_directives = 54,
  sym_include = 55,
  sym_option = 56,
  sym_plugin = 57,
  sym_pushtag = 58,
  sym_poptag = 59,
  sym_pushmeta = 60,
  sym_popmeta = 61,
  sym__dated_directives = 62,
  sym_cost_spec = 63,
  sym_cost_comp_list = 64,
  sym_cost_comp = 65,
  sym_compound_amount = 66,
  sym_incomplete_amount = 67,
  sym_price_annotation = 68,
  sym_posting = 69,
  sym_postings = 70,
  sym_tags_and_links = 71,
  sym_txn_strings = 72,
  sym_transaction = 73,
  sym_balance = 74,
  sym_close = 75,
  sym_commodity = 76,
  sym_custom = 77,
  sym_document = 78,
  sym_event = 79,
  sym_note = 80,
  sym_open = 81,
  sym_pad = 82,
  sym_price = 83,
  sym_query = 84,
  sym_currency_list = 85,
  sym_amount = 86,
  sym_amount_with_tolerance = 87,
  sym__num_expr = 88,
  sym__paren_num_expr = 89,
  sym_unary_num_expr = 90,
  sym_binary_num_expr = 91,
  aux_sym_beancount_file_repeat1 = 92,
  aux_sym_metadata_repeat1 = 93,
  aux_sym_cost_comp_list_repeat1 = 94,
  aux_sym_postings_repeat1 = 95,
  aux_sym_tags_and_links_repeat1 = 96,
  aux_sym_custom_repeat1 = 97,
  aux_sym_currency_list_repeat1 = 98,
};

static const char *ts_symbol_names[] = {
  [ts_builtin_sym_end] = "end",
  [aux_sym__skipped_lines_token1] = "_skipped_lines_token1",
  [aux_sym__skipped_lines_token2] = "_skipped_lines_token2",
  [anon_sym_COLON] = ":",
  [aux_sym__skipped_lines_token3] = "_skipped_lines_token3",
  [aux_sym_metadata_token1] = "metadata_token1",
  [anon_sym_include] = "include",
  [anon_sym_option] = "option",
  [anon_sym_plugin] = "plugin",
  [anon_sym_pushtag] = "pushtag",
  [anon_sym_poptag] = "poptag",
  [anon_sym_pushmeta] = "pushmeta",
  [anon_sym_popmeta] = "popmeta",
  [anon_sym_LBRACE] = "{",
  [anon_sym_RBRACE] = "}",
  [anon_sym_LBRACE_LBRACE] = "{{",
  [anon_sym_RBRACE_RBRACE] = "}}",
  [anon_sym_COMMA] = ",",
  [anon_sym_STAR] = "*",
  [anon_sym_POUND] = "#",
  [anon_sym_AT_AT] = "@@",
  [anon_sym_AT] = "@",
  [anon_sym_balance] = "balance",
  [anon_sym_close] = "close",
  [anon_sym_commodity] = "commodity",
  [anon_sym_custom] = "custom",
  [anon_sym_document] = "document",
  [anon_sym_event] = "event",
  [anon_sym_note] = "note",
  [anon_sym_open] = "open",
  [anon_sym_pad] = "pad",
  [anon_sym_price] = "price",
  [anon_sym_query] = "query",
  [anon_sym_TILDE] = "~",
  [anon_sym_LPAREN] = "(",
  [anon_sym_RPAREN] = ")",
  [anon_sym_DASH] = "-",
  [anon_sym_PLUS] = "+",
  [anon_sym_SLASH] = "/",
  [sym_bool] = "bool",
  [sym_date] = "date",
  [sym_key] = "key",
  [sym_tag] = "tag",
  [sym_link] = "link",
  [sym_string] = "string",
  [sym_currency] = "currency",
  [sym_number] = "number",
  [sym_flag] = "flag",
  [sym_account] = "account",
  [sym_beancount_file] = "beancount_file",
  [sym__skipped_lines] = "_skipped_lines",
  [sym__key_value_value] = "_key_value_value",
  [sym_key_value] = "key_value",
  [sym_metadata] = "metadata",
  [sym__undated_directives] = "_undated_directives",
  [sym_include] = "include",
  [sym_option] = "option",
  [sym_plugin] = "plugin",
  [sym_pushtag] = "pushtag",
  [sym_poptag] = "poptag",
  [sym_pushmeta] = "pushmeta",
  [sym_popmeta] = "popmeta",
  [sym__dated_directives] = "_dated_directives",
  [sym_cost_spec] = "cost_spec",
  [sym_cost_comp_list] = "cost_comp_list",
  [sym_cost_comp] = "cost_comp",
  [sym_compound_amount] = "compound_amount",
  [sym_incomplete_amount] = "incomplete_amount",
  [sym_price_annotation] = "price_annotation",
  [sym_posting] = "posting",
  [sym_postings] = "postings",
  [sym_tags_and_links] = "tags_and_links",
  [sym_txn_strings] = "txn_strings",
  [sym_transaction] = "transaction",
  [sym_balance] = "balance",
  [sym_close] = "close",
  [sym_commodity] = "commodity",
  [sym_custom] = "custom",
  [sym_document] = "document",
  [sym_event] = "event",
  [sym_note] = "note",
  [sym_open] = "open",
  [sym_pad] = "pad",
  [sym_price] = "price",
  [sym_query] = "query",
  [sym_currency_list] = "currency_list",
  [sym_amount] = "amount",
  [sym_amount_with_tolerance] = "amount_with_tolerance",
  [sym__num_expr] = "_num_expr",
  [sym__paren_num_expr] = "_paren_num_expr",
  [sym_unary_num_expr] = "unary_num_expr",
  [sym_binary_num_expr] = "binary_num_expr",
  [aux_sym_beancount_file_repeat1] = "beancount_file_repeat1",
  [aux_sym_metadata_repeat1] = "metadata_repeat1",
  [aux_sym_cost_comp_list_repeat1] = "cost_comp_list_repeat1",
  [aux_sym_postings_repeat1] = "postings_repeat1",
  [aux_sym_tags_and_links_repeat1] = "tags_and_links_repeat1",
  [aux_sym_custom_repeat1] = "custom_repeat1",
  [aux_sym_currency_list_repeat1] = "currency_list_repeat1",
};

static TSSymbol ts_symbol_map[] = {
  [ts_builtin_sym_end] = ts_builtin_sym_end,
  [aux_sym__skipped_lines_token1] = aux_sym__skipped_lines_token1,
  [aux_sym__skipped_lines_token2] = aux_sym__skipped_lines_token2,
  [anon_sym_COLON] = anon_sym_COLON,
  [aux_sym__skipped_lines_token3] = aux_sym__skipped_lines_token3,
  [aux_sym_metadata_token1] = aux_sym_metadata_token1,
  [anon_sym_include] = anon_sym_include,
  [anon_sym_option] = anon_sym_option,
  [anon_sym_plugin] = anon_sym_plugin,
  [anon_sym_pushtag] = anon_sym_pushtag,
  [anon_sym_poptag] = anon_sym_poptag,
  [anon_sym_pushmeta] = anon_sym_pushmeta,
  [anon_sym_popmeta] = anon_sym_popmeta,
  [anon_sym_LBRACE] = anon_sym_LBRACE,
  [anon_sym_RBRACE] = anon_sym_RBRACE,
  [anon_sym_LBRACE_LBRACE] = anon_sym_LBRACE_LBRACE,
  [anon_sym_RBRACE_RBRACE] = anon_sym_RBRACE_RBRACE,
  [anon_sym_COMMA] = anon_sym_COMMA,
  [anon_sym_STAR] = anon_sym_STAR,
  [anon_sym_POUND] = anon_sym_POUND,
  [anon_sym_AT_AT] = anon_sym_AT_AT,
  [anon_sym_AT] = anon_sym_AT,
  [anon_sym_balance] = anon_sym_balance,
  [anon_sym_close] = anon_sym_close,
  [anon_sym_commodity] = anon_sym_commodity,
  [anon_sym_custom] = anon_sym_custom,
  [anon_sym_document] = anon_sym_document,
  [anon_sym_event] = anon_sym_event,
  [anon_sym_note] = anon_sym_note,
  [anon_sym_open] = anon_sym_open,
  [anon_sym_pad] = anon_sym_pad,
  [anon_sym_price] = anon_sym_price,
  [anon_sym_query] = anon_sym_query,
  [anon_sym_TILDE] = anon_sym_TILDE,
  [anon_sym_LPAREN] = anon_sym_LPAREN,
  [anon_sym_RPAREN] = anon_sym_RPAREN,
  [anon_sym_DASH] = anon_sym_DASH,
  [anon_sym_PLUS] = anon_sym_PLUS,
  [anon_sym_SLASH] = anon_sym_SLASH,
  [sym_bool] = sym_bool,
  [sym_date] = sym_date,
  [sym_key] = sym_key,
  [sym_tag] = sym_tag,
  [sym_link] = sym_link,
  [sym_string] = sym_string,
  [sym_currency] = sym_currency,
  [sym_number] = sym_number,
  [sym_flag] = sym_flag,
  [sym_account] = sym_account,
  [sym_beancount_file] = sym_beancount_file,
  [sym__skipped_lines] = sym__skipped_lines,
  [sym__key_value_value] = sym__key_value_value,
  [sym_key_value] = sym_key_value,
  [sym_metadata] = sym_metadata,
  [sym__undated_directives] = sym__undated_directives,
  [sym_include] = sym_include,
  [sym_option] = sym_option,
  [sym_plugin] = sym_plugin,
  [sym_pushtag] = sym_pushtag,
  [sym_poptag] = sym_poptag,
  [sym_pushmeta] = sym_pushmeta,
  [sym_popmeta] = sym_popmeta,
  [sym__dated_directives] = sym__dated_directives,
  [sym_cost_spec] = sym_cost_spec,
  [sym_cost_comp_list] = sym_cost_comp_list,
  [sym_cost_comp] = sym_cost_comp,
  [sym_compound_amount] = sym_compound_amount,
  [sym_incomplete_amount] = sym_incomplete_amount,
  [sym_price_annotation] = sym_price_annotation,
  [sym_posting] = sym_posting,
  [sym_postings] = sym_postings,
  [sym_tags_and_links] = sym_tags_and_links,
  [sym_txn_strings] = sym_txn_strings,
  [sym_transaction] = sym_transaction,
  [sym_balance] = sym_balance,
  [sym_close] = sym_close,
  [sym_commodity] = sym_commodity,
  [sym_custom] = sym_custom,
  [sym_document] = sym_document,
  [sym_event] = sym_event,
  [sym_note] = sym_note,
  [sym_open] = sym_open,
  [sym_pad] = sym_pad,
  [sym_price] = sym_price,
  [sym_query] = sym_query,
  [sym_currency_list] = sym_currency_list,
  [sym_amount] = sym_amount,
  [sym_amount_with_tolerance] = sym_amount_with_tolerance,
  [sym__num_expr] = sym__num_expr,
  [sym__paren_num_expr] = sym__paren_num_expr,
  [sym_unary_num_expr] = sym_unary_num_expr,
  [sym_binary_num_expr] = sym_binary_num_expr,
  [aux_sym_beancount_file_repeat1] = aux_sym_beancount_file_repeat1,
  [aux_sym_metadata_repeat1] = aux_sym_metadata_repeat1,
  [aux_sym_cost_comp_list_repeat1] = aux_sym_cost_comp_list_repeat1,
  [aux_sym_postings_repeat1] = aux_sym_postings_repeat1,
  [aux_sym_tags_and_links_repeat1] = aux_sym_tags_and_links_repeat1,
  [aux_sym_custom_repeat1] = aux_sym_custom_repeat1,
  [aux_sym_currency_list_repeat1] = aux_sym_currency_list_repeat1,
};

static const TSSymbolMetadata ts_symbol_metadata[] = {
  [ts_builtin_sym_end] = {
    .visible = false,
    .named = true,
  },
  [aux_sym__skipped_lines_token1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym__skipped_lines_token2] = {
    .visible = false,
    .named = false,
  },
  [anon_sym_COLON] = {
    .visible = true,
    .named = false,
  },
  [aux_sym__skipped_lines_token3] = {
    .visible = false,
    .named = false,
  },
  [aux_sym_metadata_token1] = {
    .visible = false,
    .named = false,
  },
  [anon_sym_include] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_option] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_plugin] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_pushtag] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_poptag] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_pushmeta] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_popmeta] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_LBRACE] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_RBRACE] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_LBRACE_LBRACE] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_RBRACE_RBRACE] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_COMMA] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_STAR] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_POUND] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_AT_AT] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_AT] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_balance] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_close] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_commodity] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_custom] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_document] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_event] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_note] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_open] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_pad] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_price] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_query] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_TILDE] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_LPAREN] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_RPAREN] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_DASH] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_PLUS] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_SLASH] = {
    .visible = true,
    .named = false,
  },
  [sym_bool] = {
    .visible = true,
    .named = true,
  },
  [sym_date] = {
    .visible = true,
    .named = true,
  },
  [sym_key] = {
    .visible = true,
    .named = true,
  },
  [sym_tag] = {
    .visible = true,
    .named = true,
  },
  [sym_link] = {
    .visible = true,
    .named = true,
  },
  [sym_string] = {
    .visible = true,
    .named = true,
  },
  [sym_currency] = {
    .visible = true,
    .named = true,
  },
  [sym_number] = {
    .visible = true,
    .named = true,
  },
  [sym_flag] = {
    .visible = true,
    .named = true,
  },
  [sym_account] = {
    .visible = true,
    .named = true,
  },
  [sym_beancount_file] = {
    .visible = true,
    .named = true,
  },
  [sym__skipped_lines] = {
    .visible = false,
    .named = true,
  },
  [sym__key_value_value] = {
    .visible = false,
    .named = true,
  },
  [sym_key_value] = {
    .visible = true,
    .named = true,
  },
  [sym_metadata] = {
    .visible = true,
    .named = true,
  },
  [sym__undated_directives] = {
    .visible = false,
    .named = true,
  },
  [sym_include] = {
    .visible = true,
    .named = true,
  },
  [sym_option] = {
    .visible = true,
    .named = true,
  },
  [sym_plugin] = {
    .visible = true,
    .named = true,
  },
  [sym_pushtag] = {
    .visible = true,
    .named = true,
  },
  [sym_poptag] = {
    .visible = true,
    .named = true,
  },
  [sym_pushmeta] = {
    .visible = true,
    .named = true,
  },
  [sym_popmeta] = {
    .visible = true,
    .named = true,
  },
  [sym__dated_directives] = {
    .visible = false,
    .named = true,
  },
  [sym_cost_spec] = {
    .visible = true,
    .named = true,
  },
  [sym_cost_comp_list] = {
    .visible = true,
    .named = true,
  },
  [sym_cost_comp] = {
    .visible = true,
    .named = true,
  },
  [sym_compound_amount] = {
    .visible = true,
    .named = true,
  },
  [sym_incomplete_amount] = {
    .visible = true,
    .named = true,
  },
  [sym_price_annotation] = {
    .visible = true,
    .named = true,
  },
  [sym_posting] = {
    .visible = true,
    .named = true,
  },
  [sym_postings] = {
    .visible = true,
    .named = true,
  },
  [sym_tags_and_links] = {
    .visible = true,
    .named = true,
  },
  [sym_txn_strings] = {
    .visible = true,
    .named = true,
  },
  [sym_transaction] = {
    .visible = true,
    .named = true,
  },
  [sym_balance] = {
    .visible = true,
    .named = true,
  },
  [sym_close] = {
    .visible = true,
    .named = true,
  },
  [sym_commodity] = {
    .visible = true,
    .named = true,
  },
  [sym_custom] = {
    .visible = true,
    .named = true,
  },
  [sym_document] = {
    .visible = true,
    .named = true,
  },
  [sym_event] = {
    .visible = true,
    .named = true,
  },
  [sym_note] = {
    .visible = true,
    .named = true,
  },
  [sym_open] = {
    .visible = true,
    .named = true,
  },
  [sym_pad] = {
    .visible = true,
    .named = true,
  },
  [sym_price] = {
    .visible = true,
    .named = true,
  },
  [sym_query] = {
    .visible = true,
    .named = true,
  },
  [sym_currency_list] = {
    .visible = true,
    .named = true,
  },
  [sym_amount] = {
    .visible = true,
    .named = true,
  },
  [sym_amount_with_tolerance] = {
    .visible = true,
    .named = true,
  },
  [sym__num_expr] = {
    .visible = false,
    .named = true,
  },
  [sym__paren_num_expr] = {
    .visible = false,
    .named = true,
  },
  [sym_unary_num_expr] = {
    .visible = true,
    .named = true,
  },
  [sym_binary_num_expr] = {
    .visible = true,
    .named = true,
  },
  [aux_sym_beancount_file_repeat1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym_metadata_repeat1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym_cost_comp_list_repeat1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym_postings_repeat1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym_tags_and_links_repeat1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym_custom_repeat1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym_currency_list_repeat1] = {
    .visible = false,
    .named = false,
  },
};

enum {
  field_account = 1,
  field_amount = 2,
  field_booking = 3,
  field_config = 4,
  field_cost_spec = 5,
  field_currencies = 6,
  field_currency = 7,
  field_date = 8,
  field_description = 9,
  field_filename = 10,
  field_flag = 11,
  field_from_account = 12,
  field_key = 13,
  field_key_value = 14,
  field_metadata = 15,
  field_name = 16,
  field_note = 17,
  field_number_per = 18,
  field_number_total = 19,
  field_postings = 20,
  field_price_annotation = 21,
  field_query = 22,
  field_tag = 23,
  field_tags_and_links = 24,
  field_txn_strings = 25,
  field_type = 26,
  field_value = 27,
};

static const char *ts_field_names[] = {
  [0] = NULL,
  [field_account] = "account",
  [field_amount] = "amount",
  [field_booking] = "booking",
  [field_config] = "config",
  [field_cost_spec] = "cost_spec",
  [field_currencies] = "currencies",
  [field_currency] = "currency",
  [field_date] = "date",
  [field_description] = "description",
  [field_filename] = "filename",
  [field_flag] = "flag",
  [field_from_account] = "from_account",
  [field_key] = "key",
  [field_key_value] = "key_value",
  [field_metadata] = "metadata",
  [field_name] = "name",
  [field_note] = "note",
  [field_number_per] = "number_per",
  [field_number_total] = "number_total",
  [field_postings] = "postings",
  [field_price_annotation] = "price_annotation",
  [field_query] = "query",
  [field_tag] = "tag",
  [field_tags_and_links] = "tags_and_links",
  [field_txn_strings] = "txn_strings",
  [field_type] = "type",
  [field_value] = "value",
};

static const TSFieldMapSlice ts_field_map_slices[83] = {
  [1] = {.index = 0, .length = 1},
  [2] = {.index = 1, .length = 1},
  [3] = {.index = 2, .length = 1},
  [4] = {.index = 3, .length = 1},
  [5] = {.index = 4, .length = 2},
  [6] = {.index = 6, .length = 2},
  [7] = {.index = 8, .length = 2},
  [8] = {.index = 10, .length = 2},
  [9] = {.index = 12, .length = 2},
  [10] = {.index = 14, .length = 1},
  [11] = {.index = 15, .length = 3},
  [12] = {.index = 18, .length = 3},
  [13] = {.index = 21, .length = 3},
  [14] = {.index = 24, .length = 3},
  [15] = {.index = 27, .length = 3},
  [16] = {.index = 30, .length = 3},
  [17] = {.index = 33, .length = 3},
  [18] = {.index = 36, .length = 3},
  [19] = {.index = 39, .length = 3},
  [20] = {.index = 42, .length = 3},
  [21] = {.index = 45, .length = 3},
  [22] = {.index = 48, .length = 3},
  [23] = {.index = 51, .length = 3},
  [24] = {.index = 54, .length = 2},
  [25] = {.index = 56, .length = 2},
  [26] = {.index = 58, .length = 2},
  [27] = {.index = 60, .length = 2},
  [28] = {.index = 62, .length = 2},
  [29] = {.index = 64, .length = 4},
  [30] = {.index = 68, .length = 4},
  [31] = {.index = 72, .length = 4},
  [32] = {.index = 76, .length = 4},
  [33] = {.index = 80, .length = 3},
  [34] = {.index = 83, .length = 4},
  [35] = {.index = 87, .length = 4},
  [36] = {.index = 91, .length = 4},
  [37] = {.index = 95, .length = 4},
  [38] = {.index = 99, .length = 4},
  [39] = {.index = 103, .length = 4},
  [40] = {.index = 107, .length = 4},
  [41] = {.index = 111, .length = 4},
  [42] = {.index = 115, .length = 4},
  [43] = {.index = 119, .length = 4},
  [44] = {.index = 123, .length = 3},
  [45] = {.index = 126, .length = 3},
  [46] = {.index = 129, .length = 3},
  [47] = {.index = 132, .length = 3},
  [48] = {.index = 135, .length = 1},
  [49] = {.index = 136, .length = 1},
  [50] = {.index = 137, .length = 3},
  [51] = {.index = 140, .length = 3},
  [52] = {.index = 143, .length = 3},
  [53] = {.index = 146, .length = 3},
  [54] = {.index = 149, .length = 3},
  [55] = {.index = 152, .length = 3},
  [56] = {.index = 155, .length = 5},
  [57] = {.index = 160, .length = 5},
  [58] = {.index = 165, .length = 5},
  [59] = {.index = 170, .length = 5},
  [60] = {.index = 175, .length = 5},
  [61] = {.index = 180, .length = 4},
  [62] = {.index = 184, .length = 4},
  [63] = {.index = 188, .length = 4},
  [64] = {.index = 192, .length = 4},
  [65] = {.index = 196, .length = 4},
  [66] = {.index = 200, .length = 4},
  [67] = {.index = 204, .length = 1},
  [68] = {.index = 205, .length = 2},
  [69] = {.index = 207, .length = 4},
  [70] = {.index = 211, .length = 4},
  [71] = {.index = 215, .length = 4},
  [72] = {.index = 219, .length = 4},
  [73] = {.index = 223, .length = 6},
  [74] = {.index = 229, .length = 5},
  [75] = {.index = 234, .length = 5},
  [76] = {.index = 239, .length = 5},
  [77] = {.index = 244, .length = 5},
  [78] = {.index = 249, .length = 2},
  [79] = {.index = 251, .length = 2},
  [80] = {.index = 253, .length = 5},
  [81] = {.index = 258, .length = 6},
  [82] = {.index = 264, .length = 3},
};

static const TSFieldMapEntry ts_field_map_entries[] = {
  [0] =
    {field_name, 1},
  [1] =
    {field_tag, 1},
  [2] =
    {field_key_value, 1},
  [3] =
    {field_key, 1},
  [4] =
    {field_key, 1},
    {field_value, 2},
  [6] =
    {field_config, 2},
    {field_name, 1},
  [8] =
    {field_account, 2},
    {field_date, 0},
  [10] =
    {field_currency, 2},
    {field_date, 0},
  [12] =
    {field_date, 0},
    {field_name, 2},
  [14] =
    {field_account, 1},
  [15] =
    {field_date, 0},
    {field_flag, 1},
    {field_postings, 2},
  [18] =
    {field_account, 2},
    {field_amount, 3},
    {field_date, 0},
  [21] =
    {field_account, 2},
    {field_date, 0},
    {field_metadata, 3},
  [24] =
    {field_currency, 2},
    {field_date, 0},
    {field_metadata, 3},
  [27] =
    {field_date, 0},
    {field_metadata, 3},
    {field_name, 2},
  [30] =
    {field_account, 2},
    {field_date, 0},
    {field_filename, 3},
  [33] =
    {field_date, 0},
    {field_description, 3},
    {field_type, 2},
  [36] =
    {field_account, 2},
    {field_date, 0},
    {field_note, 3},
  [39] =
    {field_account, 2},
    {field_booking, 3},
    {field_date, 0},
  [42] =
    {field_account, 2},
    {field_currencies, 3},
    {field_date, 0},
  [45] =
    {field_account, 2},
    {field_date, 0},
    {field_from_account, 3},
  [48] =
    {field_amount, 3},
    {field_currency, 2},
    {field_date, 0},
  [51] =
    {field_date, 0},
    {field_name, 2},
    {field_query, 3},
  [54] =
    {field_account, 2},
    {field_flag, 1},
  [56] =
    {field_account, 1},
    {field_metadata, 2},
  [58] =
    {field_account, 1},
    {field_cost_spec, 2},
  [60] =
    {field_account, 1},
    {field_amount, 2},
  [62] =
    {field_account, 1},
    {field_price_annotation, 2},
  [64] =
    {field_date, 0},
    {field_flag, 1},
    {field_metadata, 2},
    {field_postings, 3},
  [68] =
    {field_date, 0},
    {field_flag, 1},
    {field_postings, 3},
    {field_tags_and_links, 2},
  [72] =
    {field_date, 0},
    {field_flag, 1},
    {field_postings, 3},
    {field_txn_strings, 2},
  [76] =
    {field_account, 2},
    {field_amount, 3},
    {field_date, 0},
    {field_metadata, 4},
  [80] =
    {field_date, 0},
    {field_metadata, 4},
    {field_name, 2},
  [83] =
    {field_account, 2},
    {field_date, 0},
    {field_filename, 3},
    {field_metadata, 4},
  [87] =
    {field_account, 2},
    {field_date, 0},
    {field_filename, 3},
    {field_tags_and_links, 4},
  [91] =
    {field_date, 0},
    {field_description, 3},
    {field_metadata, 4},
    {field_type, 2},
  [95] =
    {field_account, 2},
    {field_date, 0},
    {field_metadata, 4},
    {field_note, 3},
  [99] =
    {field_account, 2},
    {field_booking, 3},
    {field_date, 0},
    {field_metadata, 4},
  [103] =
    {field_account, 2},
    {field_booking, 4},
    {field_currencies, 3},
    {field_date, 0},
  [107] =
    {field_account, 2},
    {field_currencies, 3},
    {field_date, 0},
    {field_metadata, 4},
  [111] =
    {field_account, 2},
    {field_date, 0},
    {field_from_account, 3},
    {field_metadata, 4},
  [115] =
    {field_amount, 3},
    {field_currency, 2},
    {field_date, 0},
    {field_metadata, 4},
  [119] =
    {field_date, 0},
    {field_metadata, 4},
    {field_name, 2},
    {field_query, 3},
  [123] =
    {field_account, 2},
    {field_flag, 1},
    {field_metadata, 3},
  [126] =
    {field_account, 2},
    {field_cost_spec, 3},
    {field_flag, 1},
  [129] =
    {field_account, 2},
    {field_amount, 3},
    {field_flag, 1},
  [132] =
    {field_account, 2},
    {field_flag, 1},
    {field_price_annotation, 3},
  [135] =
    {field_currency, 0},
  [136] =
    {field_number_per, 0},
  [137] =
    {field_account, 1},
    {field_cost_spec, 2},
    {field_metadata, 3},
  [140] =
    {field_account, 1},
    {field_cost_spec, 2},
    {field_price_annotation, 3},
  [143] =
    {field_account, 1},
    {field_amount, 2},
    {field_metadata, 3},
  [146] =
    {field_account, 1},
    {field_amount, 2},
    {field_cost_spec, 3},
  [149] =
    {field_account, 1},
    {field_amount, 2},
    {field_price_annotation, 3},
  [152] =
    {field_account, 1},
    {field_metadata, 3},
    {field_price_annotation, 2},
  [155] =
    {field_date, 0},
    {field_flag, 1},
    {field_metadata, 3},
    {field_postings, 4},
    {field_tags_and_links, 2},
  [160] =
    {field_date, 0},
    {field_flag, 1},
    {field_metadata, 3},
    {field_postings, 4},
    {field_txn_strings, 2},
  [165] =
    {field_date, 0},
    {field_flag, 1},
    {field_postings, 4},
    {field_tags_and_links, 3},
    {field_txn_strings, 2},
  [170] =
    {field_account, 2},
    {field_date, 0},
    {field_filename, 3},
    {field_metadata, 5},
    {field_tags_and_links, 4},
  [175] =
    {field_account, 2},
    {field_booking, 4},
    {field_currencies, 3},
    {field_date, 0},
    {field_metadata, 5},
  [180] =
    {field_account, 2},
    {field_cost_spec, 3},
    {field_flag, 1},
    {field_metadata, 4},
  [184] =
    {field_account, 2},
    {field_cost_spec, 3},
    {field_flag, 1},
    {field_price_annotation, 4},
  [188] =
    {field_account, 2},
    {field_amount, 3},
    {field_flag, 1},
    {field_metadata, 4},
  [192] =
    {field_account, 2},
    {field_amount, 3},
    {field_cost_spec, 4},
    {field_flag, 1},
  [196] =
    {field_account, 2},
    {field_amount, 3},
    {field_flag, 1},
    {field_price_annotation, 4},
  [200] =
    {field_account, 2},
    {field_flag, 1},
    {field_metadata, 4},
    {field_price_annotation, 3},
  [204] =
    {field_currency, 1},
  [205] =
    {field_currency, 1},
    {field_number_per, 0},
  [207] =
    {field_account, 1},
    {field_cost_spec, 2},
    {field_metadata, 4},
    {field_price_annotation, 3},
  [211] =
    {field_account, 1},
    {field_amount, 2},
    {field_cost_spec, 3},
    {field_metadata, 4},
  [215] =
    {field_account, 1},
    {field_amount, 2},
    {field_cost_spec, 3},
    {field_price_annotation, 4},
  [219] =
    {field_account, 1},
    {field_amount, 2},
    {field_metadata, 4},
    {field_price_annotation, 3},
  [223] =
    {field_date, 0},
    {field_flag, 1},
    {field_metadata, 4},
    {field_postings, 5},
    {field_tags_and_links, 3},
    {field_txn_strings, 2},
  [229] =
    {field_account, 2},
    {field_cost_spec, 3},
    {field_flag, 1},
    {field_metadata, 5},
    {field_price_annotation, 4},
  [234] =
    {field_account, 2},
    {field_amount, 3},
    {field_cost_spec, 4},
    {field_flag, 1},
    {field_metadata, 5},
  [239] =
    {field_account, 2},
    {field_amount, 3},
    {field_cost_spec, 4},
    {field_flag, 1},
    {field_price_annotation, 5},
  [244] =
    {field_account, 2},
    {field_amount, 3},
    {field_flag, 1},
    {field_metadata, 5},
    {field_price_annotation, 4},
  [249] =
    {field_currency, 2},
    {field_number_total, 1},
  [251] =
    {field_currency, 2},
    {field_number_per, 0},
  [253] =
    {field_account, 1},
    {field_amount, 2},
    {field_cost_spec, 3},
    {field_metadata, 5},
    {field_price_annotation, 4},
  [258] =
    {field_account, 2},
    {field_amount, 3},
    {field_cost_spec, 4},
    {field_flag, 1},
    {field_metadata, 6},
    {field_price_annotation, 5},
  [264] =
    {field_currency, 3},
    {field_number_per, 0},
    {field_number_total, 2},
};

static TSSymbol ts_alias_sequences[83][MAX_ALIAS_SEQUENCE_LENGTH] = {
  [0] = {0},
};

static bool ts_lex(TSLexer *lexer, TSStateId state) {
  START_LEXER();
  eof = lexer->eof(lexer);
  switch (state) {
    case 0:
      if (eof) ADVANCE(156);
      if (lookahead == '\n') ADVANCE(160);
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == '#') ADVANCE(178);
      if (lookahead == '(') ADVANCE(193);
      if (lookahead == ')') ADVANCE(194);
      if (lookahead == '*') ADVANCE(177);
      if (lookahead == '+') ADVANCE(196);
      if (lookahead == ',') ADVANCE(176);
      if (lookahead == '-') ADVANCE(195);
      if (lookahead == '/') ADVANCE(197);
      if (lookahead == ':') ADVANCE(161);
      if (lookahead == ';') ADVANCE(162);
      if (lookahead == '@') ADVANCE(180);
      if (lookahead == '^') ADVANCE(152);
      if (lookahead == 'b') ADVANCE(45);
      if (lookahead == 'c') ADVANCE(79);
      if (lookahead == 'd') ADVANCE(94);
      if (lookahead == 'e') ADVANCE(117);
      if (lookahead == 'i') ADVANCE(90);
      if (lookahead == 'n') ADVANCE(95);
      if (lookahead == 'o') ADVANCE(100);
      if (lookahead == 'p') ADVANCE(46);
      if (lookahead == 'q') ADVANCE(114);
      if (lookahead == '{') ADVANCE(171);
      if (lookahead == '}') ADVANCE(173);
      if (lookahead == '~') ADVANCE(192);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(0)
      if (lookahead == '!' ||
          lookahead == '%' ||
          lookahead == '&' ||
          lookahead == '?') ADVANCE(266);
      if (lookahead == 'C' ||
          lookahead == 'M' ||
          lookahead == 'P' ||
          ('R' <= lookahead && lookahead <= 'U')) ADVANCE(267);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(260);
      if (lookahead != 0 &&
          (lookahead < 0 || '>' < lookahead) &&
          (lookahead < '[' || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 1:
      if (lookahead == '\n') ADVANCE(160);
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == '#') ADVANCE(153);
      if (lookahead == '(') ADVANCE(193);
      if (lookahead == ')') ADVANCE(194);
      if (lookahead == '*') ADVANCE(177);
      if (lookahead == '+') ADVANCE(196);
      if (lookahead == '-') ADVANCE(195);
      if (lookahead == '/') ADVANCE(197);
      if (lookahead == '@') ADVANCE(180);
      if (lookahead == '^') ADVANCE(152);
      if (lookahead == '{') ADVANCE(171);
      if (lookahead == '}') ADVANCE(172);
      if (lookahead == '~') ADVANCE(192);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(1)
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(261);
      if (('A' <= lookahead && lookahead <= 'Z')) ADVANCE(143);
      if (('a' <= lookahead && lookahead <= 'z')) ADVANCE(151);
      END_STATE();
    case 2:
      if (lookahead == '\n') ADVANCE(160);
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == '#') ADVANCE(153);
      if (lookahead == '(') ADVANCE(193);
      if (lookahead == '*') ADVANCE(177);
      if (lookahead == '+') ADVANCE(196);
      if (lookahead == '-') ADVANCE(195);
      if (lookahead == '/') ADVANCE(197);
      if (lookahead == 'F') ADVANCE(32);
      if (lookahead == 'T') ADVANCE(33);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(2)
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(260);
      if (('A' <= lookahead && lookahead <= 'Z')) ADVANCE(34);
      if (lookahead != 0 &&
          (lookahead < 0 || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 3:
      if (lookahead == '\n') ADVANCE(160);
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == '(') ADVANCE(193);
      if (lookahead == '+') ADVANCE(196);
      if (lookahead == '-') ADVANCE(195);
      if (lookahead == 'F') ADVANCE(35);
      if (lookahead == 'T') ADVANCE(38);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(3)
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(260);
      if (lookahead != 0 &&
          (lookahead < 0 || '@' < lookahead) &&
          (lookahead < '[' || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 4:
      if (lookahead == '\n') ADVANCE(159);
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == '#') ADVANCE(178);
      if (lookahead == '(') ADVANCE(193);
      if (lookahead == '*') ADVANCE(177);
      if (lookahead == '+') ADVANCE(196);
      if (lookahead == '-') ADVANCE(195);
      if (lookahead == '/') ADVANCE(197);
      if (lookahead == '}') ADVANCE(120);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(4)
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(260);
      if (('A' <= lookahead && lookahead <= 'Z')) ADVANCE(143);
      END_STATE();
    case 5:
      if (lookahead == '\n') ADVANCE(159);
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == '#') ADVANCE(153);
      if (lookahead == '(') ADVANCE(193);
      if (lookahead == '+') ADVANCE(196);
      if (lookahead == '-') ADVANCE(195);
      if (lookahead == 'F') ADVANCE(32);
      if (lookahead == 'T') ADVANCE(33);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(5)
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(260);
      if (('A' <= lookahead && lookahead <= 'Z')) ADVANCE(34);
      if (lookahead != 0 &&
          (lookahead < 0 || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 6:
      if (lookahead == '\n') ADVANCE(159);
      if (lookahead == '#') ADVANCE(178);
      if (lookahead == ')') ADVANCE(194);
      if (lookahead == '*') ADVANCE(177);
      if (lookahead == '+') ADVANCE(196);
      if (lookahead == ',') ADVANCE(176);
      if (lookahead == '-') ADVANCE(195);
      if (lookahead == '/') ADVANCE(197);
      if (lookahead == '}') ADVANCE(173);
      if (lookahead == '~') ADVANCE(192);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(6)
      if (('A' <= lookahead && lookahead <= 'Z')) ADVANCE(143);
      END_STATE();
    case 7:
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == '#') ADVANCE(178);
      if (lookahead == '(') ADVANCE(193);
      if (lookahead == '*') ADVANCE(177);
      if (lookahead == '+') ADVANCE(196);
      if (lookahead == '-') ADVANCE(195);
      if (lookahead == '}') ADVANCE(172);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(7)
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(260);
      if (('A' <= lookahead && lookahead <= 'Z')) ADVANCE(143);
      END_STATE();
    case 8:
      if (lookahead == '"') ADVANCE(205);
      if (lookahead != 0) ADVANCE(8);
      END_STATE();
    case 9:
      if (lookahead == '#') ADVANCE(268);
      if (lookahead == ';') ADVANCE(162);
      if (lookahead == '^') ADVANCE(152);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(9)
      if (lookahead == '!' ||
          lookahead == '%' ||
          lookahead == '&' ||
          lookahead == '*' ||
          lookahead == '?') ADVANCE(266);
      if (lookahead == 'C' ||
          lookahead == 'M' ||
          lookahead == 'P' ||
          ('R' <= lookahead && lookahead <= 'U')) ADVANCE(267);
      if (lookahead != 0 &&
          (lookahead < 0 || '@' < lookahead) &&
          (lookahead < '[' || 127 < lookahead)) ADVANCE(41);
      if (('a' <= lookahead && lookahead <= 'z')) ADVANCE(151);
      END_STATE();
    case 10:
      if (lookahead == ',') ADVANCE(10);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(261);
      END_STATE();
    case 11:
      if (lookahead == '-') ADVANCE(42);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(150);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(234);
      END_STATE();
    case 12:
      if (lookahead == '-') ADVANCE(13);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(124);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(209);
      END_STATE();
    case 13:
      if (lookahead == '-') ADVANCE(11);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(123);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(207);
      END_STATE();
    case 14:
      if (lookahead == '-') ADVANCE(15);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(125);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(211);
      END_STATE();
    case 15:
      if (lookahead == '-') ADVANCE(12);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(126);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(208);
      END_STATE();
    case 16:
      if (lookahead == '-') ADVANCE(17);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(127);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(213);
      END_STATE();
    case 17:
      if (lookahead == '-') ADVANCE(14);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(128);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(210);
      END_STATE();
    case 18:
      if (lookahead == '-') ADVANCE(19);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(129);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(215);
      END_STATE();
    case 19:
      if (lookahead == '-') ADVANCE(16);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(130);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(212);
      END_STATE();
    case 20:
      if (lookahead == '-') ADVANCE(21);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(131);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(217);
      END_STATE();
    case 21:
      if (lookahead == '-') ADVANCE(18);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(132);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(214);
      END_STATE();
    case 22:
      if (lookahead == '-') ADVANCE(23);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(133);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(219);
      END_STATE();
    case 23:
      if (lookahead == '-') ADVANCE(20);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(134);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(216);
      END_STATE();
    case 24:
      if (lookahead == '-') ADVANCE(25);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(135);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(221);
      END_STATE();
    case 25:
      if (lookahead == '-') ADVANCE(22);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(136);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(218);
      END_STATE();
    case 26:
      if (lookahead == '-') ADVANCE(27);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(137);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(223);
      END_STATE();
    case 27:
      if (lookahead == '-') ADVANCE(24);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(138);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(220);
      END_STATE();
    case 28:
      if (lookahead == '-') ADVANCE(29);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(139);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(226);
      END_STATE();
    case 29:
      if (lookahead == '-') ADVANCE(26);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(140);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(222);
      END_STATE();
    case 30:
      if (lookahead == '-') ADVANCE(31);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(141);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(232);
      END_STATE();
    case 31:
      if (lookahead == '-') ADVANCE(28);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(142);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(225);
      END_STATE();
    case 32:
      if (lookahead == '-') ADVANCE(30);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'A') ADVANCE(227);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(144);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('B' <= lookahead && lookahead <= 'Z')) ADVANCE(229);
      END_STATE();
    case 33:
      if (lookahead == '-') ADVANCE(30);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'R') ADVANCE(228);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(144);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(229);
      END_STATE();
    case 34:
      if (lookahead == '-') ADVANCE(30);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(144);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(229);
      END_STATE();
    case 35:
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'A') ADVANCE(37);
      if (lookahead != 0 &&
          (lookahead < 0 || ',' < lookahead) &&
          lookahead != '.' &&
          lookahead != '/' &&
          (lookahead < ';' || '@' < lookahead) &&
          (lookahead < '[' || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 36:
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'E') ADVANCE(200);
      if (lookahead != 0 &&
          (lookahead < 0 || ',' < lookahead) &&
          lookahead != '.' &&
          lookahead != '/' &&
          (lookahead < ';' || '@' < lookahead) &&
          (lookahead < '[' || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 37:
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'L') ADVANCE(39);
      if (lookahead != 0 &&
          (lookahead < 0 || ',' < lookahead) &&
          lookahead != '.' &&
          lookahead != '/' &&
          (lookahead < ';' || '@' < lookahead) &&
          (lookahead < '[' || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 38:
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'R') ADVANCE(40);
      if (lookahead != 0 &&
          (lookahead < 0 || ',' < lookahead) &&
          lookahead != '.' &&
          lookahead != '/' &&
          (lookahead < ';' || '@' < lookahead) &&
          (lookahead < '[' || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 39:
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'S') ADVANCE(36);
      if (lookahead != 0 &&
          (lookahead < 0 || ',' < lookahead) &&
          lookahead != '.' &&
          lookahead != '/' &&
          (lookahead < ';' || '@' < lookahead) &&
          (lookahead < '[' || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 40:
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'U') ADVANCE(36);
      if (lookahead != 0 &&
          (lookahead < 0 || ',' < lookahead) &&
          lookahead != '.' &&
          lookahead != '/' &&
          (lookahead < ';' || '@' < lookahead) &&
          (lookahead < '[' || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 41:
      if (lookahead == ':') ADVANCE(154);
      if (lookahead != 0 &&
          (lookahead < 0 || ',' < lookahead) &&
          lookahead != '.' &&
          lookahead != '/' &&
          (lookahead < ';' || '@' < lookahead) &&
          (lookahead < '[' || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 42:
      if (lookahead == ':') ADVANCE(154);
      if (lookahead != 0 &&
          (lookahead < 0 || ',' < lookahead) &&
          (lookahead < '.' || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(233);
      END_STATE();
    case 43:
      if (lookahead == ':') ADVANCE(202);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(43);
      END_STATE();
    case 44:
      if (lookahead == ';') ADVANCE(162);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(44)
      if (lookahead == '!' ||
          lookahead == '#' ||
          lookahead == '%' ||
          lookahead == '&' ||
          lookahead == '*' ||
          lookahead == '?') ADVANCE(266);
      if (lookahead == 'C' ||
          lookahead == 'M' ||
          lookahead == 'P' ||
          ('R' <= lookahead && lookahead <= 'U')) ADVANCE(267);
      if (lookahead != 0 &&
          (lookahead < 0 || '@' < lookahead) &&
          (lookahead < '[' || 127 < lookahead)) ADVANCE(41);
      if (('a' <= lookahead && lookahead <= 'z')) ADVANCE(151);
      END_STATE();
    case 45:
      if (lookahead == 'a') ADVANCE(78);
      END_STATE();
    case 46:
      if (lookahead == 'a') ADVANCE(56);
      if (lookahead == 'l') ADVANCE(113);
      if (lookahead == 'o') ADVANCE(101);
      if (lookahead == 'r') ADVANCE(74);
      if (lookahead == 'u') ADVANCE(103);
      END_STATE();
    case 47:
      if (lookahead == 'a') ADVANCE(170);
      END_STATE();
    case 48:
      if (lookahead == 'a') ADVANCE(169);
      END_STATE();
    case 49:
      if (lookahead == 'a') ADVANCE(70);
      END_STATE();
    case 50:
      if (lookahead == 'a') ADVANCE(71);
      END_STATE();
    case 51:
      if (lookahead == 'a') ADVANCE(93);
      END_STATE();
    case 52:
      if (lookahead == 'c') ADVANCE(80);
      END_STATE();
    case 53:
      if (lookahead == 'c') ADVANCE(115);
      END_STATE();
    case 54:
      if (lookahead == 'c') ADVANCE(62);
      END_STATE();
    case 55:
      if (lookahead == 'c') ADVANCE(63);
      END_STATE();
    case 56:
      if (lookahead == 'd') ADVANCE(189);
      END_STATE();
    case 57:
      if (lookahead == 'd') ADVANCE(76);
      END_STATE();
    case 58:
      if (lookahead == 'd') ADVANCE(64);
      END_STATE();
    case 59:
      if (lookahead == 'e') ADVANCE(102);
      END_STATE();
    case 60:
      if (lookahead == 'e') ADVANCE(187);
      END_STATE();
    case 61:
      if (lookahead == 'e') ADVANCE(182);
      END_STATE();
    case 62:
      if (lookahead == 'e') ADVANCE(190);
      END_STATE();
    case 63:
      if (lookahead == 'e') ADVANCE(181);
      END_STATE();
    case 64:
      if (lookahead == 'e') ADVANCE(164);
      END_STATE();
    case 65:
      if (lookahead == 'e') ADVANCE(91);
      END_STATE();
    case 66:
      if (lookahead == 'e') ADVANCE(87);
      if (lookahead == 't') ADVANCE(77);
      END_STATE();
    case 67:
      if (lookahead == 'e') ADVANCE(110);
      END_STATE();
    case 68:
      if (lookahead == 'e') ADVANCE(92);
      END_STATE();
    case 69:
      if (lookahead == 'e') ADVANCE(112);
      END_STATE();
    case 70:
      if (lookahead == 'g') ADVANCE(168);
      END_STATE();
    case 71:
      if (lookahead == 'g') ADVANCE(167);
      END_STATE();
    case 72:
      if (lookahead == 'g') ADVANCE(75);
      END_STATE();
    case 73:
      if (lookahead == 'h') ADVANCE(85);
      END_STATE();
    case 74:
      if (lookahead == 'i') ADVANCE(54);
      END_STATE();
    case 75:
      if (lookahead == 'i') ADVANCE(89);
      END_STATE();
    case 76:
      if (lookahead == 'i') ADVANCE(108);
      END_STATE();
    case 77:
      if (lookahead == 'i') ADVANCE(98);
      END_STATE();
    case 78:
      if (lookahead == 'l') ADVANCE(51);
      END_STATE();
    case 79:
      if (lookahead == 'l') ADVANCE(97);
      if (lookahead == 'o') ADVANCE(82);
      if (lookahead == 'u') ADVANCE(104);
      END_STATE();
    case 80:
      if (lookahead == 'l') ADVANCE(116);
      END_STATE();
    case 81:
      if (lookahead == 'm') ADVANCE(184);
      END_STATE();
    case 82:
      if (lookahead == 'm') ADVANCE(83);
      END_STATE();
    case 83:
      if (lookahead == 'm') ADVANCE(96);
      END_STATE();
    case 84:
      if (lookahead == 'm') ADVANCE(67);
      if (lookahead == 't') ADVANCE(49);
      END_STATE();
    case 85:
      if (lookahead == 'm') ADVANCE(69);
      if (lookahead == 't') ADVANCE(50);
      END_STATE();
    case 86:
      if (lookahead == 'm') ADVANCE(68);
      END_STATE();
    case 87:
      if (lookahead == 'n') ADVANCE(188);
      END_STATE();
    case 88:
      if (lookahead == 'n') ADVANCE(165);
      END_STATE();
    case 89:
      if (lookahead == 'n') ADVANCE(166);
      END_STATE();
    case 90:
      if (lookahead == 'n') ADVANCE(52);
      END_STATE();
    case 91:
      if (lookahead == 'n') ADVANCE(106);
      END_STATE();
    case 92:
      if (lookahead == 'n') ADVANCE(107);
      END_STATE();
    case 93:
      if (lookahead == 'n') ADVANCE(55);
      END_STATE();
    case 94:
      if (lookahead == 'o') ADVANCE(53);
      END_STATE();
    case 95:
      if (lookahead == 'o') ADVANCE(109);
      END_STATE();
    case 96:
      if (lookahead == 'o') ADVANCE(57);
      END_STATE();
    case 97:
      if (lookahead == 'o') ADVANCE(105);
      END_STATE();
    case 98:
      if (lookahead == 'o') ADVANCE(88);
      END_STATE();
    case 99:
      if (lookahead == 'o') ADVANCE(81);
      END_STATE();
    case 100:
      if (lookahead == 'p') ADVANCE(66);
      END_STATE();
    case 101:
      if (lookahead == 'p') ADVANCE(84);
      END_STATE();
    case 102:
      if (lookahead == 'r') ADVANCE(118);
      END_STATE();
    case 103:
      if (lookahead == 's') ADVANCE(73);
      END_STATE();
    case 104:
      if (lookahead == 's') ADVANCE(111);
      END_STATE();
    case 105:
      if (lookahead == 's') ADVANCE(61);
      END_STATE();
    case 106:
      if (lookahead == 't') ADVANCE(186);
      END_STATE();
    case 107:
      if (lookahead == 't') ADVANCE(185);
      END_STATE();
    case 108:
      if (lookahead == 't') ADVANCE(119);
      END_STATE();
    case 109:
      if (lookahead == 't') ADVANCE(60);
      END_STATE();
    case 110:
      if (lookahead == 't') ADVANCE(47);
      END_STATE();
    case 111:
      if (lookahead == 't') ADVANCE(99);
      END_STATE();
    case 112:
      if (lookahead == 't') ADVANCE(48);
      END_STATE();
    case 113:
      if (lookahead == 'u') ADVANCE(72);
      END_STATE();
    case 114:
      if (lookahead == 'u') ADVANCE(59);
      END_STATE();
    case 115:
      if (lookahead == 'u') ADVANCE(86);
      END_STATE();
    case 116:
      if (lookahead == 'u') ADVANCE(58);
      END_STATE();
    case 117:
      if (lookahead == 'v') ADVANCE(65);
      END_STATE();
    case 118:
      if (lookahead == 'y') ADVANCE(191);
      END_STATE();
    case 119:
      if (lookahead == 'y') ADVANCE(183);
      END_STATE();
    case 120:
      if (lookahead == '}') ADVANCE(175);
      END_STATE();
    case 121:
      if (lookahead == '-' ||
          lookahead == '/') ADVANCE(145);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(121);
      END_STATE();
    case 122:
      if (lookahead == '-' ||
          lookahead == '/') ADVANCE(147);
      END_STATE();
    case 123:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(150);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(256);
      END_STATE();
    case 124:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(123);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(235);
      END_STATE();
    case 125:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(126);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(238);
      END_STATE();
    case 126:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(124);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(236);
      END_STATE();
    case 127:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(128);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(240);
      END_STATE();
    case 128:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(125);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(237);
      END_STATE();
    case 129:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(130);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(242);
      END_STATE();
    case 130:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(127);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(239);
      END_STATE();
    case 131:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(132);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(244);
      END_STATE();
    case 132:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(129);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(241);
      END_STATE();
    case 133:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(134);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(246);
      END_STATE();
    case 134:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(131);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(243);
      END_STATE();
    case 135:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(136);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(248);
      END_STATE();
    case 136:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(133);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(245);
      END_STATE();
    case 137:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(138);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(250);
      END_STATE();
    case 138:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(135);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(247);
      END_STATE();
    case 139:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(140);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(252);
      END_STATE();
    case 140:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(137);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(249);
      END_STATE();
    case 141:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(142);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(254);
      END_STATE();
    case 142:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(139);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(251);
      END_STATE();
    case 143:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(144);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(255);
      END_STATE();
    case 144:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(141);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(253);
      END_STATE();
    case 145:
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(201);
      END_STATE();
    case 146:
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(122);
      END_STATE();
    case 147:
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(121);
      END_STATE();
    case 148:
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(146);
      END_STATE();
    case 149:
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(148);
      END_STATE();
    case 150:
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(206);
      END_STATE();
    case 151:
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(43);
      END_STATE();
    case 152:
      if (('-' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(204);
      END_STATE();
    case 153:
      if (('-' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(203);
      END_STATE();
    case 154:
      if (lookahead != 0 &&
          (lookahead < 0 || '/' < lookahead) &&
          (lookahead < ':' || '@' < lookahead) &&
          (lookahead < '[' || 127 < lookahead)) ADVANCE(269);
      END_STATE();
    case 155:
      if (eof) ADVANCE(156);
      if (lookahead == '\n') ADVANCE(159);
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == ':') ADVANCE(161);
      if (lookahead == ';') ADVANCE(162);
      if (lookahead == 'b') ADVANCE(45);
      if (lookahead == 'c') ADVANCE(79);
      if (lookahead == 'd') ADVANCE(94);
      if (lookahead == 'e') ADVANCE(117);
      if (lookahead == 'i') ADVANCE(90);
      if (lookahead == 'n') ADVANCE(95);
      if (lookahead == 'o') ADVANCE(100);
      if (lookahead == 'p') ADVANCE(46);
      if (lookahead == 'q') ADVANCE(114);
      if (lookahead == '}') ADVANCE(120);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(155)
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(149);
      if (('!' <= lookahead && lookahead <= '#') ||
          lookahead == '%' ||
          lookahead == '&' ||
          lookahead == '*' ||
          lookahead == '?' ||
          lookahead == 'C' ||
          lookahead == 'M' ||
          lookahead == 'P' ||
          ('R' <= lookahead && lookahead <= 'U')) ADVANCE(266);
      END_STATE();
    case 156:
      ACCEPT_TOKEN(ts_builtin_sym_end);
      END_STATE();
    case 157:
      ACCEPT_TOKEN(aux_sym__skipped_lines_token1);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') ADVANCE(157);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(158);
      END_STATE();
    case 158:
      ACCEPT_TOKEN(aux_sym__skipped_lines_token1);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(158);
      END_STATE();
    case 159:
      ACCEPT_TOKEN(aux_sym__skipped_lines_token2);
      END_STATE();
    case 160:
      ACCEPT_TOKEN(aux_sym__skipped_lines_token2);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') ADVANCE(163);
      END_STATE();
    case 161:
      ACCEPT_TOKEN(anon_sym_COLON);
      END_STATE();
    case 162:
      ACCEPT_TOKEN(aux_sym__skipped_lines_token3);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(162);
      END_STATE();
    case 163:
      ACCEPT_TOKEN(aux_sym_metadata_token1);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') ADVANCE(163);
      END_STATE();
    case 164:
      ACCEPT_TOKEN(anon_sym_include);
      END_STATE();
    case 165:
      ACCEPT_TOKEN(anon_sym_option);
      END_STATE();
    case 166:
      ACCEPT_TOKEN(anon_sym_plugin);
      END_STATE();
    case 167:
      ACCEPT_TOKEN(anon_sym_pushtag);
      END_STATE();
    case 168:
      ACCEPT_TOKEN(anon_sym_poptag);
      END_STATE();
    case 169:
      ACCEPT_TOKEN(anon_sym_pushmeta);
      END_STATE();
    case 170:
      ACCEPT_TOKEN(anon_sym_popmeta);
      END_STATE();
    case 171:
      ACCEPT_TOKEN(anon_sym_LBRACE);
      if (lookahead == '{') ADVANCE(174);
      END_STATE();
    case 172:
      ACCEPT_TOKEN(anon_sym_RBRACE);
      END_STATE();
    case 173:
      ACCEPT_TOKEN(anon_sym_RBRACE);
      if (lookahead == '}') ADVANCE(175);
      END_STATE();
    case 174:
      ACCEPT_TOKEN(anon_sym_LBRACE_LBRACE);
      END_STATE();
    case 175:
      ACCEPT_TOKEN(anon_sym_RBRACE_RBRACE);
      END_STATE();
    case 176:
      ACCEPT_TOKEN(anon_sym_COMMA);
      END_STATE();
    case 177:
      ACCEPT_TOKEN(anon_sym_STAR);
      END_STATE();
    case 178:
      ACCEPT_TOKEN(anon_sym_POUND);
      END_STATE();
    case 179:
      ACCEPT_TOKEN(anon_sym_AT_AT);
      END_STATE();
    case 180:
      ACCEPT_TOKEN(anon_sym_AT);
      if (lookahead == '@') ADVANCE(179);
      END_STATE();
    case 181:
      ACCEPT_TOKEN(anon_sym_balance);
      END_STATE();
    case 182:
      ACCEPT_TOKEN(anon_sym_close);
      END_STATE();
    case 183:
      ACCEPT_TOKEN(anon_sym_commodity);
      END_STATE();
    case 184:
      ACCEPT_TOKEN(anon_sym_custom);
      END_STATE();
    case 185:
      ACCEPT_TOKEN(anon_sym_document);
      END_STATE();
    case 186:
      ACCEPT_TOKEN(anon_sym_event);
      END_STATE();
    case 187:
      ACCEPT_TOKEN(anon_sym_note);
      END_STATE();
    case 188:
      ACCEPT_TOKEN(anon_sym_open);
      END_STATE();
    case 189:
      ACCEPT_TOKEN(anon_sym_pad);
      END_STATE();
    case 190:
      ACCEPT_TOKEN(anon_sym_price);
      END_STATE();
    case 191:
      ACCEPT_TOKEN(anon_sym_query);
      END_STATE();
    case 192:
      ACCEPT_TOKEN(anon_sym_TILDE);
      END_STATE();
    case 193:
      ACCEPT_TOKEN(anon_sym_LPAREN);
      END_STATE();
    case 194:
      ACCEPT_TOKEN(anon_sym_RPAREN);
      END_STATE();
    case 195:
      ACCEPT_TOKEN(anon_sym_DASH);
      END_STATE();
    case 196:
      ACCEPT_TOKEN(anon_sym_PLUS);
      END_STATE();
    case 197:
      ACCEPT_TOKEN(anon_sym_SLASH);
      END_STATE();
    case 198:
      ACCEPT_TOKEN(sym_bool);
      if (lookahead == '-') ADVANCE(29);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(139);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(226);
      END_STATE();
    case 199:
      ACCEPT_TOKEN(sym_bool);
      if (lookahead == '-') ADVANCE(26);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(140);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(222);
      END_STATE();
    case 200:
      ACCEPT_TOKEN(sym_bool);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead != 0 &&
          (lookahead < 0 || ',' < lookahead) &&
          lookahead != '.' &&
          lookahead != '/' &&
          (lookahead < ';' || '@' < lookahead) &&
          (lookahead < '[' || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 201:
      ACCEPT_TOKEN(sym_date);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(201);
      END_STATE();
    case 202:
      ACCEPT_TOKEN(sym_key);
      END_STATE();
    case 203:
      ACCEPT_TOKEN(sym_tag);
      if (('-' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(203);
      END_STATE();
    case 204:
      ACCEPT_TOKEN(sym_link);
      if (('-' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(204);
      END_STATE();
    case 205:
      ACCEPT_TOKEN(sym_string);
      END_STATE();
    case 206:
      ACCEPT_TOKEN(sym_currency);
      END_STATE();
    case 207:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(42);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(150);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(234);
      END_STATE();
    case 208:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(13);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(124);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(209);
      END_STATE();
    case 209:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(11);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(123);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(207);
      END_STATE();
    case 210:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(15);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(125);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(211);
      END_STATE();
    case 211:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(12);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(126);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(208);
      END_STATE();
    case 212:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(17);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(127);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(213);
      END_STATE();
    case 213:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(14);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(128);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(210);
      END_STATE();
    case 214:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(19);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(129);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(215);
      END_STATE();
    case 215:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(16);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(130);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(212);
      END_STATE();
    case 216:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(21);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(131);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(217);
      END_STATE();
    case 217:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(18);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(132);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(214);
      END_STATE();
    case 218:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(23);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(133);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(219);
      END_STATE();
    case 219:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(20);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(134);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(216);
      END_STATE();
    case 220:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(25);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(135);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(221);
      END_STATE();
    case 221:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(22);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(136);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(218);
      END_STATE();
    case 222:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(27);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(137);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(223);
      END_STATE();
    case 223:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(24);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(138);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(220);
      END_STATE();
    case 224:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(29);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'E') ADVANCE(199);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(139);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(226);
      END_STATE();
    case 225:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(29);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(139);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(226);
      END_STATE();
    case 226:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(26);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(140);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(222);
      END_STATE();
    case 227:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(31);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'L') ADVANCE(231);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(141);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(232);
      END_STATE();
    case 228:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(31);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'U') ADVANCE(230);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(141);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(232);
      END_STATE();
    case 229:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(31);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(141);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(232);
      END_STATE();
    case 230:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(28);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'E') ADVANCE(198);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(142);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(225);
      END_STATE();
    case 231:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(28);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'S') ADVANCE(224);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(142);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(225);
      END_STATE();
    case 232:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(28);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(142);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(225);
      END_STATE();
    case 233:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead != 0 &&
          (lookahead < 0 || ',' < lookahead) &&
          lookahead != '.' &&
          lookahead != '/' &&
          (lookahead < ';' || '@' < lookahead) &&
          (lookahead < '[' || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 234:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead != 0 &&
          (lookahead < 0 || ',' < lookahead) &&
          (lookahead < '.' || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(233);
      END_STATE();
    case 235:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(150);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(256);
      END_STATE();
    case 236:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(123);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(235);
      END_STATE();
    case 237:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(126);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(238);
      END_STATE();
    case 238:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(124);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(236);
      END_STATE();
    case 239:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(128);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(240);
      END_STATE();
    case 240:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(125);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(237);
      END_STATE();
    case 241:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(130);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(242);
      END_STATE();
    case 242:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(127);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(239);
      END_STATE();
    case 243:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(132);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(244);
      END_STATE();
    case 244:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(129);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(241);
      END_STATE();
    case 245:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(134);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(246);
      END_STATE();
    case 246:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(131);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(243);
      END_STATE();
    case 247:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(136);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(248);
      END_STATE();
    case 248:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(133);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(245);
      END_STATE();
    case 249:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(138);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(250);
      END_STATE();
    case 250:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(135);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(247);
      END_STATE();
    case 251:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(140);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(252);
      END_STATE();
    case 252:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(137);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(249);
      END_STATE();
    case 253:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(142);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(254);
      END_STATE();
    case 254:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(139);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(251);
      END_STATE();
    case 255:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(141);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(253);
      END_STATE();
    case 256:
      ACCEPT_TOKEN(sym_currency);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(206);
      END_STATE();
    case 257:
      ACCEPT_TOKEN(sym_number);
      if (lookahead == ',') ADVANCE(262);
      if (lookahead == '-' ||
          lookahead == '/') ADVANCE(265);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(261);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(264);
      END_STATE();
    case 258:
      ACCEPT_TOKEN(sym_number);
      if (lookahead == ',') ADVANCE(262);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(257);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(264);
      END_STATE();
    case 259:
      ACCEPT_TOKEN(sym_number);
      if (lookahead == ',') ADVANCE(262);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(258);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(264);
      END_STATE();
    case 260:
      ACCEPT_TOKEN(sym_number);
      if (lookahead == ',') ADVANCE(262);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(259);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(264);
      END_STATE();
    case 261:
      ACCEPT_TOKEN(sym_number);
      if (lookahead == ',') ADVANCE(262);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(261);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(264);
      END_STATE();
    case 262:
      ACCEPT_TOKEN(sym_number);
      if (lookahead == ',') ADVANCE(10);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(261);
      END_STATE();
    case 263:
      ACCEPT_TOKEN(sym_number);
      if (lookahead == '-' ||
          lookahead == '/') ADVANCE(145);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(263);
      END_STATE();
    case 264:
      ACCEPT_TOKEN(sym_number);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(264);
      END_STATE();
    case 265:
      ACCEPT_TOKEN(sym_number);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(263);
      END_STATE();
    case 266:
      ACCEPT_TOKEN(sym_flag);
      END_STATE();
    case 267:
      ACCEPT_TOKEN(sym_flag);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead != 0 &&
          (lookahead < 0 || ',' < lookahead) &&
          lookahead != '.' &&
          lookahead != '/' &&
          (lookahead < ';' || '@' < lookahead) &&
          (lookahead < '[' || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 268:
      ACCEPT_TOKEN(sym_flag);
      if (('-' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(203);
      END_STATE();
    case 269:
      ACCEPT_TOKEN(sym_account);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead != 0 &&
          (lookahead < 0 || ',' < lookahead) &&
          lookahead != '.' &&
          lookahead != '/' &&
          (lookahead < ';' || '@' < lookahead) &&
          (lookahead < '[' || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(269);
      END_STATE();
    default:
      return false;
  }
}

static TSLexMode ts_lex_modes[STATE_COUNT] = {
  [0] = {.lex_state = 0},
  [1] = {.lex_state = 155},
  [2] = {.lex_state = 155},
  [3] = {.lex_state = 155},
  [4] = {.lex_state = 1},
  [5] = {.lex_state = 1},
  [6] = {.lex_state = 3},
  [7] = {.lex_state = 3},
  [8] = {.lex_state = 2},
  [9] = {.lex_state = 4},
  [10] = {.lex_state = 7},
  [11] = {.lex_state = 5},
  [12] = {.lex_state = 3},
  [13] = {.lex_state = 4},
  [14] = {.lex_state = 155},
  [15] = {.lex_state = 155},
  [16] = {.lex_state = 155},
  [17] = {.lex_state = 155},
  [18] = {.lex_state = 155},
  [19] = {.lex_state = 155},
  [20] = {.lex_state = 2},
  [21] = {.lex_state = 2},
  [22] = {.lex_state = 2},
  [23] = {.lex_state = 155},
  [24] = {.lex_state = 155},
  [25] = {.lex_state = 155},
  [26] = {.lex_state = 2},
  [27] = {.lex_state = 155},
  [28] = {.lex_state = 155},
  [29] = {.lex_state = 155},
  [30] = {.lex_state = 155},
  [31] = {.lex_state = 155},
  [32] = {.lex_state = 155},
  [33] = {.lex_state = 155},
  [34] = {.lex_state = 155},
  [35] = {.lex_state = 155},
  [36] = {.lex_state = 155},
  [37] = {.lex_state = 155},
  [38] = {.lex_state = 155},
  [39] = {.lex_state = 155},
  [40] = {.lex_state = 155},
  [41] = {.lex_state = 155},
  [42] = {.lex_state = 155},
  [43] = {.lex_state = 155},
  [44] = {.lex_state = 155},
  [45] = {.lex_state = 155},
  [46] = {.lex_state = 155},
  [47] = {.lex_state = 155},
  [48] = {.lex_state = 155},
  [49] = {.lex_state = 155},
  [50] = {.lex_state = 155},
  [51] = {.lex_state = 155},
  [52] = {.lex_state = 155},
  [53] = {.lex_state = 155},
  [54] = {.lex_state = 155},
  [55] = {.lex_state = 155},
  [56] = {.lex_state = 155},
  [57] = {.lex_state = 155},
  [58] = {.lex_state = 155},
  [59] = {.lex_state = 2},
  [60] = {.lex_state = 155},
  [61] = {.lex_state = 155},
  [62] = {.lex_state = 155},
  [63] = {.lex_state = 155},
  [64] = {.lex_state = 155},
  [65] = {.lex_state = 155},
  [66] = {.lex_state = 155},
  [67] = {.lex_state = 155},
  [68] = {.lex_state = 155},
  [69] = {.lex_state = 6},
  [70] = {.lex_state = 1},
  [71] = {.lex_state = 155},
  [72] = {.lex_state = 6},
  [73] = {.lex_state = 1},
  [74] = {.lex_state = 6},
  [75] = {.lex_state = 6},
  [76] = {.lex_state = 1},
  [77] = {.lex_state = 1},
  [78] = {.lex_state = 1},
  [79] = {.lex_state = 1},
  [80] = {.lex_state = 1},
  [81] = {.lex_state = 0},
  [82] = {.lex_state = 1},
  [83] = {.lex_state = 1},
  [84] = {.lex_state = 0},
  [85] = {.lex_state = 3},
  [86] = {.lex_state = 1},
  [87] = {.lex_state = 1},
  [88] = {.lex_state = 6},
  [89] = {.lex_state = 1},
  [90] = {.lex_state = 1},
  [91] = {.lex_state = 1},
  [92] = {.lex_state = 1},
  [93] = {.lex_state = 1},
  [94] = {.lex_state = 1},
  [95] = {.lex_state = 1},
  [96] = {.lex_state = 1},
  [97] = {.lex_state = 1},
  [98] = {.lex_state = 1},
  [99] = {.lex_state = 1},
  [100] = {.lex_state = 1},
  [101] = {.lex_state = 1},
  [102] = {.lex_state = 1},
  [103] = {.lex_state = 1},
  [104] = {.lex_state = 1},
  [105] = {.lex_state = 0},
  [106] = {.lex_state = 0},
  [107] = {.lex_state = 9},
  [108] = {.lex_state = 1},
  [109] = {.lex_state = 0},
  [110] = {.lex_state = 0},
  [111] = {.lex_state = 1},
  [112] = {.lex_state = 0},
  [113] = {.lex_state = 0},
  [114] = {.lex_state = 4},
  [115] = {.lex_state = 0},
  [116] = {.lex_state = 0},
  [117] = {.lex_state = 1},
  [118] = {.lex_state = 1},
  [119] = {.lex_state = 1},
  [120] = {.lex_state = 0},
  [121] = {.lex_state = 0},
  [122] = {.lex_state = 0},
  [123] = {.lex_state = 1},
  [124] = {.lex_state = 1},
  [125] = {.lex_state = 0},
  [126] = {.lex_state = 44},
  [127] = {.lex_state = 1},
  [128] = {.lex_state = 1},
  [129] = {.lex_state = 1},
  [130] = {.lex_state = 1},
  [131] = {.lex_state = 1},
  [132] = {.lex_state = 0},
  [133] = {.lex_state = 0},
  [134] = {.lex_state = 0},
  [135] = {.lex_state = 0},
  [136] = {.lex_state = 0},
  [137] = {.lex_state = 0},
  [138] = {.lex_state = 0},
  [139] = {.lex_state = 0},
  [140] = {.lex_state = 0},
  [141] = {.lex_state = 1},
  [142] = {.lex_state = 0},
  [143] = {.lex_state = 0},
  [144] = {.lex_state = 0},
  [145] = {.lex_state = 0},
  [146] = {.lex_state = 0},
  [147] = {.lex_state = 0},
  [148] = {.lex_state = 0},
  [149] = {.lex_state = 0},
  [150] = {.lex_state = 0},
  [151] = {.lex_state = 0},
  [152] = {.lex_state = 0},
  [153] = {.lex_state = 0},
  [154] = {.lex_state = 0},
  [155] = {.lex_state = 0},
  [156] = {.lex_state = 0},
  [157] = {.lex_state = 0},
  [158] = {.lex_state = 0},
  [159] = {.lex_state = 1},
  [160] = {.lex_state = 0},
  [161] = {.lex_state = 0},
  [162] = {.lex_state = 0},
  [163] = {.lex_state = 0},
  [164] = {.lex_state = 0},
  [165] = {.lex_state = 0},
  [166] = {.lex_state = 44},
  [167] = {.lex_state = 0},
  [168] = {.lex_state = 0},
  [169] = {.lex_state = 0},
  [170] = {.lex_state = 0},
  [171] = {.lex_state = 0},
  [172] = {.lex_state = 0},
  [173] = {.lex_state = 0},
  [174] = {.lex_state = 0},
  [175] = {.lex_state = 1},
  [176] = {.lex_state = 0},
  [177] = {.lex_state = 0},
  [178] = {.lex_state = 0},
  [179] = {.lex_state = 0},
  [180] = {.lex_state = 0},
  [181] = {.lex_state = 0},
  [182] = {.lex_state = 0},
  [183] = {.lex_state = 0},
  [184] = {.lex_state = 1},
  [185] = {.lex_state = 1},
  [186] = {.lex_state = 0},
  [187] = {.lex_state = 0},
  [188] = {.lex_state = 0},
  [189] = {.lex_state = 0},
  [190] = {.lex_state = 0},
  [191] = {.lex_state = 0},
  [192] = {.lex_state = 0},
  [193] = {.lex_state = 0},
  [194] = {.lex_state = 0},
  [195] = {.lex_state = 0},
  [196] = {.lex_state = 0},
  [197] = {.lex_state = 0},
  [198] = {.lex_state = 0},
  [199] = {.lex_state = 1},
  [200] = {.lex_state = 0},
  [201] = {.lex_state = 155},
  [202] = {.lex_state = 0},
  [203] = {.lex_state = 155},
  [204] = {.lex_state = 0},
  [205] = {.lex_state = 155},
  [206] = {.lex_state = 0},
  [207] = {.lex_state = 155},
  [208] = {.lex_state = 155},
  [209] = {.lex_state = 155},
  [210] = {.lex_state = 155},
  [211] = {.lex_state = 1},
  [212] = {.lex_state = 155},
  [213] = {.lex_state = 0},
  [214] = {.lex_state = 0},
  [215] = {.lex_state = 0},
  [216] = {.lex_state = 0},
  [217] = {.lex_state = 1},
  [218] = {.lex_state = 155},
  [219] = {.lex_state = 155},
  [220] = {.lex_state = 155},
  [221] = {.lex_state = 0},
  [222] = {.lex_state = 155},
  [223] = {.lex_state = 0},
  [224] = {.lex_state = 155},
  [225] = {.lex_state = 0},
  [226] = {.lex_state = 155},
  [227] = {.lex_state = 155},
  [228] = {.lex_state = 155},
  [229] = {.lex_state = 155},
  [230] = {.lex_state = 155},
  [231] = {.lex_state = 0},
  [232] = {.lex_state = 0},
  [233] = {.lex_state = 155},
  [234] = {.lex_state = 155},
  [235] = {.lex_state = 155},
  [236] = {.lex_state = 155},
  [237] = {.lex_state = 155},
  [238] = {.lex_state = 155},
  [239] = {.lex_state = 155},
  [240] = {.lex_state = 0},
  [241] = {.lex_state = 1},
  [242] = {.lex_state = 155},
  [243] = {.lex_state = 157},
  [244] = {.lex_state = 0},
  [245] = {.lex_state = 155},
  [246] = {.lex_state = 1},
  [247] = {.lex_state = 155},
  [248] = {.lex_state = 0},
  [249] = {.lex_state = 0},
  [250] = {.lex_state = 155},
  [251] = {.lex_state = 155},
  [252] = {.lex_state = 155},
  [253] = {.lex_state = 155},
  [254] = {.lex_state = 155},
  [255] = {.lex_state = 0},
  [256] = {.lex_state = 155},
  [257] = {.lex_state = 155},
  [258] = {.lex_state = 0},
  [259] = {.lex_state = 1},
  [260] = {.lex_state = 155},
  [261] = {.lex_state = 1},
  [262] = {.lex_state = 1},
  [263] = {.lex_state = 0},
  [264] = {.lex_state = 0},
  [265] = {.lex_state = 0},
  [266] = {.lex_state = 155},
};

static uint16_t ts_parse_table[LARGE_STATE_COUNT][SYMBOL_COUNT] = {
  [0] = {
    [ts_builtin_sym_end] = ACTIONS(1),
    [aux_sym__skipped_lines_token2] = ACTIONS(1),
    [anon_sym_COLON] = ACTIONS(1),
    [aux_sym__skipped_lines_token3] = ACTIONS(1),
    [aux_sym_metadata_token1] = ACTIONS(1),
    [anon_sym_include] = ACTIONS(1),
    [anon_sym_option] = ACTIONS(1),
    [anon_sym_plugin] = ACTIONS(1),
    [anon_sym_pushtag] = ACTIONS(1),
    [anon_sym_poptag] = ACTIONS(1),
    [anon_sym_pushmeta] = ACTIONS(1),
    [anon_sym_popmeta] = ACTIONS(1),
    [anon_sym_LBRACE] = ACTIONS(1),
    [anon_sym_RBRACE] = ACTIONS(1),
    [anon_sym_LBRACE_LBRACE] = ACTIONS(1),
    [anon_sym_RBRACE_RBRACE] = ACTIONS(1),
    [anon_sym_COMMA] = ACTIONS(1),
    [anon_sym_STAR] = ACTIONS(1),
    [anon_sym_POUND] = ACTIONS(1),
    [anon_sym_AT_AT] = ACTIONS(1),
    [anon_sym_AT] = ACTIONS(1),
    [anon_sym_balance] = ACTIONS(1),
    [anon_sym_close] = ACTIONS(1),
    [anon_sym_commodity] = ACTIONS(1),
    [anon_sym_custom] = ACTIONS(1),
    [anon_sym_document] = ACTIONS(1),
    [anon_sym_event] = ACTIONS(1),
    [anon_sym_note] = ACTIONS(1),
    [anon_sym_open] = ACTIONS(1),
    [anon_sym_pad] = ACTIONS(1),
    [anon_sym_price] = ACTIONS(1),
    [anon_sym_query] = ACTIONS(1),
    [anon_sym_TILDE] = ACTIONS(1),
    [anon_sym_LPAREN] = ACTIONS(1),
    [anon_sym_RPAREN] = ACTIONS(1),
    [anon_sym_DASH] = ACTIONS(1),
    [anon_sym_PLUS] = ACTIONS(1),
    [anon_sym_SLASH] = ACTIONS(1),
    [sym_date] = ACTIONS(1),
    [sym_link] = ACTIONS(1),
    [sym_string] = ACTIONS(1),
    [sym_number] = ACTIONS(1),
    [sym_flag] = ACTIONS(1),
    [sym_account] = ACTIONS(1),
  },
  [1] = {
    [sym_beancount_file] = STATE(258),
    [sym__skipped_lines] = STATE(3),
    [sym__undated_directives] = STATE(3),
    [sym_include] = STATE(3),
    [sym_option] = STATE(3),
    [sym_plugin] = STATE(3),
    [sym_pushtag] = STATE(3),
    [sym_poptag] = STATE(3),
    [sym_pushmeta] = STATE(3),
    [sym_popmeta] = STATE(3),
    [sym__dated_directives] = STATE(3),
    [sym_transaction] = STATE(3),
    [sym_balance] = STATE(3),
    [sym_close] = STATE(3),
    [sym_commodity] = STATE(3),
    [sym_custom] = STATE(3),
    [sym_document] = STATE(3),
    [sym_event] = STATE(3),
    [sym_note] = STATE(3),
    [sym_open] = STATE(3),
    [sym_pad] = STATE(3),
    [sym_price] = STATE(3),
    [sym_query] = STATE(3),
    [aux_sym_beancount_file_repeat1] = STATE(3),
    [ts_builtin_sym_end] = ACTIONS(3),
    [aux_sym__skipped_lines_token2] = ACTIONS(5),
    [anon_sym_COLON] = ACTIONS(7),
    [aux_sym__skipped_lines_token3] = ACTIONS(9),
    [anon_sym_include] = ACTIONS(11),
    [anon_sym_option] = ACTIONS(13),
    [anon_sym_plugin] = ACTIONS(15),
    [anon_sym_pushtag] = ACTIONS(17),
    [anon_sym_poptag] = ACTIONS(19),
    [anon_sym_pushmeta] = ACTIONS(21),
    [anon_sym_popmeta] = ACTIONS(23),
    [sym_date] = ACTIONS(25),
    [sym_flag] = ACTIONS(7),
  },
};

static uint16_t ts_small_parse_table[] = {
  [0] = 13,
    ACTIONS(27), 1,
      ts_builtin_sym_end,
    ACTIONS(29), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(35), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(38), 1,
      anon_sym_include,
    ACTIONS(41), 1,
      anon_sym_option,
    ACTIONS(44), 1,
      anon_sym_plugin,
    ACTIONS(47), 1,
      anon_sym_pushtag,
    ACTIONS(50), 1,
      anon_sym_poptag,
    ACTIONS(53), 1,
      anon_sym_pushmeta,
    ACTIONS(56), 1,
      anon_sym_popmeta,
    ACTIONS(59), 1,
      sym_date,
    ACTIONS(32), 2,
      anon_sym_COLON,
      sym_flag,
    STATE(2), 23,
      sym__skipped_lines,
      sym__undated_directives,
      sym_include,
      sym_option,
      sym_plugin,
      sym_pushtag,
      sym_poptag,
      sym_pushmeta,
      sym_popmeta,
      sym__dated_directives,
      sym_transaction,
      sym_balance,
      sym_close,
      sym_commodity,
      sym_custom,
      sym_document,
      sym_event,
      sym_note,
      sym_open,
      sym_pad,
      sym_price,
      sym_query,
      aux_sym_beancount_file_repeat1,
  [63] = 13,
    ACTIONS(9), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(11), 1,
      anon_sym_include,
    ACTIONS(13), 1,
      anon_sym_option,
    ACTIONS(15), 1,
      anon_sym_plugin,
    ACTIONS(17), 1,
      anon_sym_pushtag,
    ACTIONS(19), 1,
      anon_sym_poptag,
    ACTIONS(21), 1,
      anon_sym_pushmeta,
    ACTIONS(23), 1,
      anon_sym_popmeta,
    ACTIONS(25), 1,
      sym_date,
    ACTIONS(62), 1,
      ts_builtin_sym_end,
    ACTIONS(64), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(7), 2,
      anon_sym_COLON,
      sym_flag,
    STATE(2), 23,
      sym__skipped_lines,
      sym__undated_directives,
      sym_include,
      sym_option,
      sym_plugin,
      sym_pushtag,
      sym_poptag,
      sym_pushmeta,
      sym_popmeta,
      sym__dated_directives,
      sym_transaction,
      sym_balance,
      sym_close,
      sym_commodity,
      sym_custom,
      sym_document,
      sym_event,
      sym_note,
      sym_open,
      sym_pad,
      sym_price,
      sym_query,
      aux_sym_beancount_file_repeat1,
  [126] = 16,
    ACTIONS(66), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(68), 1,
      aux_sym_metadata_token1,
    ACTIONS(71), 1,
      anon_sym_LBRACE,
    ACTIONS(73), 1,
      anon_sym_LBRACE_LBRACE,
    ACTIONS(75), 1,
      anon_sym_AT_AT,
    ACTIONS(77), 1,
      anon_sym_AT,
    ACTIONS(79), 1,
      anon_sym_LPAREN,
    ACTIONS(83), 1,
      sym_currency,
    ACTIONS(85), 1,
      sym_number,
    STATE(84), 1,
      sym_incomplete_amount,
    STATE(110), 1,
      sym_cost_spec,
    STATE(161), 1,
      sym_price_annotation,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(192), 1,
      sym_metadata,
    ACTIONS(81), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(76), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [179] = 16,
    ACTIONS(71), 1,
      anon_sym_LBRACE,
    ACTIONS(73), 1,
      anon_sym_LBRACE_LBRACE,
    ACTIONS(75), 1,
      anon_sym_AT_AT,
    ACTIONS(77), 1,
      anon_sym_AT,
    ACTIONS(79), 1,
      anon_sym_LPAREN,
    ACTIONS(83), 1,
      sym_currency,
    ACTIONS(85), 1,
      sym_number,
    ACTIONS(87), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(89), 1,
      aux_sym_metadata_token1,
    STATE(81), 1,
      sym_incomplete_amount,
    STATE(109), 1,
      sym_cost_spec,
    STATE(139), 1,
      sym_price_annotation,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(187), 1,
      sym_metadata,
    ACTIONS(81), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(76), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [232] = 11,
    ACTIONS(92), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(96), 1,
      anon_sym_LPAREN,
    ACTIONS(100), 1,
      sym_bool,
    ACTIONS(104), 1,
      sym_number,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(260), 1,
      sym_metadata,
    ACTIONS(98), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(12), 2,
      sym_amount,
      aux_sym_custom_repeat1,
    ACTIONS(102), 3,
      sym_date,
      sym_string,
      sym_account,
    STATE(59), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [273] = 11,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(96), 1,
      anon_sym_LPAREN,
    ACTIONS(104), 1,
      sym_number,
    ACTIONS(106), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(108), 1,
      sym_bool,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(227), 1,
      sym_metadata,
    ACTIONS(98), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(6), 2,
      sym_amount,
      aux_sym_custom_repeat1,
    ACTIONS(110), 3,
      sym_date,
      sym_string,
      sym_account,
    STATE(59), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [314] = 9,
    ACTIONS(79), 1,
      anon_sym_LPAREN,
    ACTIONS(112), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(114), 1,
      aux_sym_metadata_token1,
    ACTIONS(120), 1,
      sym_number,
    ACTIONS(81), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    ACTIONS(116), 2,
      sym_bool,
      sym_currency,
    STATE(196), 2,
      sym__key_value_value,
      sym_amount,
    ACTIONS(118), 4,
      sym_date,
      sym_tag,
      sym_string,
      sym_account,
    STATE(108), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [351] = 11,
    ACTIONS(122), 1,
      anon_sym_RBRACE_RBRACE,
    ACTIONS(126), 1,
      anon_sym_POUND,
    ACTIONS(128), 1,
      anon_sym_LPAREN,
    ACTIONS(132), 1,
      sym_currency,
    ACTIONS(134), 1,
      sym_number,
    STATE(136), 1,
      sym_cost_comp,
    STATE(170), 1,
      sym_compound_amount,
    STATE(205), 1,
      sym_cost_comp_list,
    ACTIONS(130), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    ACTIONS(124), 3,
      anon_sym_STAR,
      sym_date,
      sym_string,
    STATE(88), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [391] = 11,
    ACTIONS(122), 1,
      anon_sym_RBRACE,
    ACTIONS(126), 1,
      anon_sym_POUND,
    ACTIONS(128), 1,
      anon_sym_LPAREN,
    ACTIONS(132), 1,
      sym_currency,
    ACTIONS(134), 1,
      sym_number,
    STATE(136), 1,
      sym_cost_comp,
    STATE(170), 1,
      sym_compound_amount,
    STATE(211), 1,
      sym_cost_comp_list,
    ACTIONS(130), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    ACTIONS(124), 3,
      anon_sym_STAR,
      sym_date,
      sym_string,
    STATE(88), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [431] = 8,
    ACTIONS(114), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(128), 1,
      anon_sym_LPAREN,
    ACTIONS(140), 1,
      sym_number,
    ACTIONS(130), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    ACTIONS(136), 2,
      sym_bool,
      sym_currency,
    STATE(208), 2,
      sym__key_value_value,
      sym_amount,
    ACTIONS(138), 4,
      sym_date,
      sym_tag,
      sym_string,
      sym_account,
    STATE(114), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [465] = 9,
    ACTIONS(142), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(144), 1,
      aux_sym_metadata_token1,
    ACTIONS(146), 1,
      anon_sym_LPAREN,
    ACTIONS(152), 1,
      sym_bool,
    ACTIONS(158), 1,
      sym_number,
    ACTIONS(149), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(12), 2,
      sym_amount,
      aux_sym_custom_repeat1,
    ACTIONS(155), 3,
      sym_date,
      sym_string,
      sym_account,
    STATE(59), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [500] = 9,
    ACTIONS(126), 1,
      anon_sym_POUND,
    ACTIONS(128), 1,
      anon_sym_LPAREN,
    ACTIONS(132), 1,
      sym_currency,
    ACTIONS(134), 1,
      sym_number,
    STATE(170), 1,
      sym_compound_amount,
    STATE(174), 1,
      sym_cost_comp,
    ACTIONS(130), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    ACTIONS(124), 3,
      anon_sym_STAR,
      sym_date,
      sym_string,
    STATE(88), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [534] = 1,
    ACTIONS(161), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [550] = 1,
    ACTIONS(163), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [566] = 1,
    ACTIONS(165), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [582] = 1,
    ACTIONS(167), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [598] = 1,
    ACTIONS(169), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [614] = 1,
    ACTIONS(171), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [630] = 3,
    ACTIONS(177), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(173), 4,
      aux_sym__skipped_lines_token2,
      sym_bool,
      sym_currency,
      sym_number,
    ACTIONS(175), 7,
      aux_sym_metadata_token1,
      anon_sym_LPAREN,
      anon_sym_DASH,
      anon_sym_PLUS,
      sym_date,
      sym_string,
      sym_account,
  [650] = 2,
    ACTIONS(173), 4,
      aux_sym__skipped_lines_token2,
      sym_bool,
      sym_currency,
      sym_number,
    ACTIONS(175), 9,
      aux_sym_metadata_token1,
      anon_sym_STAR,
      anon_sym_LPAREN,
      anon_sym_DASH,
      anon_sym_PLUS,
      anon_sym_SLASH,
      sym_date,
      sym_string,
      sym_account,
  [668] = 2,
    ACTIONS(179), 4,
      aux_sym__skipped_lines_token2,
      sym_bool,
      sym_currency,
      sym_number,
    ACTIONS(181), 9,
      aux_sym_metadata_token1,
      anon_sym_STAR,
      anon_sym_LPAREN,
      anon_sym_DASH,
      anon_sym_PLUS,
      anon_sym_SLASH,
      sym_date,
      sym_string,
      sym_account,
  [686] = 1,
    ACTIONS(183), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [702] = 1,
    ACTIONS(185), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [718] = 1,
    ACTIONS(187), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [734] = 2,
    ACTIONS(189), 4,
      aux_sym__skipped_lines_token2,
      sym_bool,
      sym_currency,
      sym_number,
    ACTIONS(191), 9,
      aux_sym_metadata_token1,
      anon_sym_STAR,
      anon_sym_LPAREN,
      anon_sym_DASH,
      anon_sym_PLUS,
      anon_sym_SLASH,
      sym_date,
      sym_string,
      sym_account,
  [752] = 1,
    ACTIONS(193), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [768] = 1,
    ACTIONS(195), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [784] = 1,
    ACTIONS(197), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [800] = 1,
    ACTIONS(199), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [816] = 1,
    ACTIONS(201), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [832] = 1,
    ACTIONS(203), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [848] = 1,
    ACTIONS(205), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [864] = 1,
    ACTIONS(207), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [880] = 1,
    ACTIONS(209), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [896] = 1,
    ACTIONS(211), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [912] = 1,
    ACTIONS(213), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [928] = 1,
    ACTIONS(215), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [944] = 1,
    ACTIONS(217), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [960] = 1,
    ACTIONS(219), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [976] = 1,
    ACTIONS(221), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [992] = 1,
    ACTIONS(223), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1008] = 1,
    ACTIONS(225), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1024] = 1,
    ACTIONS(227), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1040] = 1,
    ACTIONS(229), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1056] = 1,
    ACTIONS(231), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1072] = 1,
    ACTIONS(233), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1088] = 1,
    ACTIONS(235), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1104] = 1,
    ACTIONS(237), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1120] = 1,
    ACTIONS(239), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1136] = 1,
    ACTIONS(241), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1152] = 1,
    ACTIONS(243), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1168] = 1,
    ACTIONS(245), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1184] = 1,
    ACTIONS(247), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1200] = 1,
    ACTIONS(249), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1216] = 1,
    ACTIONS(251), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1232] = 1,
    ACTIONS(253), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1248] = 1,
    ACTIONS(255), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1264] = 5,
    ACTIONS(263), 1,
      sym_currency,
    ACTIONS(177), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(261), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    ACTIONS(257), 3,
      aux_sym__skipped_lines_token2,
      sym_bool,
      sym_number,
    ACTIONS(259), 5,
      aux_sym_metadata_token1,
      anon_sym_LPAREN,
      sym_date,
      sym_string,
      sym_account,
  [1288] = 1,
    ACTIONS(265), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1304] = 1,
    ACTIONS(267), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1320] = 1,
    ACTIONS(269), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1336] = 1,
    ACTIONS(271), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1352] = 1,
    ACTIONS(273), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1368] = 1,
    ACTIONS(275), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1384] = 1,
    ACTIONS(277), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1400] = 1,
    ACTIONS(279), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1416] = 1,
    ACTIONS(281), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token2,
      anon_sym_COLON,
      aux_sym__skipped_lines_token3,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
      sym_flag,
  [1432] = 2,
    ACTIONS(189), 1,
      anon_sym_RBRACE,
    ACTIONS(191), 11,
      aux_sym__skipped_lines_token2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
      anon_sym_STAR,
      anon_sym_POUND,
      anon_sym_TILDE,
      anon_sym_RPAREN,
      anon_sym_DASH,
      anon_sym_PLUS,
      anon_sym_SLASH,
      sym_currency,
  [1449] = 8,
    ACTIONS(79), 1,
      anon_sym_LPAREN,
    ACTIONS(83), 1,
      sym_currency,
    ACTIONS(85), 1,
      sym_number,
    ACTIONS(283), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(285), 1,
      aux_sym_metadata_token1,
    STATE(197), 1,
      sym_incomplete_amount,
    ACTIONS(81), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(76), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1478] = 12,
    ACTIONS(287), 1,
      anon_sym_balance,
    ACTIONS(289), 1,
      anon_sym_close,
    ACTIONS(291), 1,
      anon_sym_commodity,
    ACTIONS(293), 1,
      anon_sym_custom,
    ACTIONS(295), 1,
      anon_sym_document,
    ACTIONS(297), 1,
      anon_sym_event,
    ACTIONS(299), 1,
      anon_sym_note,
    ACTIONS(301), 1,
      anon_sym_open,
    ACTIONS(303), 1,
      anon_sym_pad,
    ACTIONS(305), 1,
      anon_sym_price,
    ACTIONS(307), 1,
      anon_sym_query,
    ACTIONS(309), 1,
      sym_flag,
  [1515] = 3,
    ACTIONS(173), 1,
      anon_sym_RBRACE,
    ACTIONS(311), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(175), 9,
      aux_sym__skipped_lines_token2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
      anon_sym_POUND,
      anon_sym_TILDE,
      anon_sym_RPAREN,
      anon_sym_DASH,
      anon_sym_PLUS,
      sym_currency,
  [1534] = 10,
    ACTIONS(313), 1,
      aux_sym_metadata_token1,
    ACTIONS(317), 1,
      sym_string,
    STATE(83), 1,
      sym_txn_strings,
    STATE(112), 1,
      sym_tags_and_links,
    STATE(128), 1,
      aux_sym_tags_and_links_repeat1,
    STATE(143), 1,
      sym_metadata,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(218), 1,
      sym_postings,
    ACTIONS(315), 2,
      sym_tag,
      sym_link,
    STATE(149), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [1567] = 2,
    ACTIONS(179), 1,
      anon_sym_RBRACE,
    ACTIONS(181), 11,
      aux_sym__skipped_lines_token2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
      anon_sym_STAR,
      anon_sym_POUND,
      anon_sym_TILDE,
      anon_sym_RPAREN,
      anon_sym_DASH,
      anon_sym_PLUS,
      anon_sym_SLASH,
      sym_currency,
  [1584] = 2,
    ACTIONS(173), 1,
      anon_sym_RBRACE,
    ACTIONS(175), 11,
      aux_sym__skipped_lines_token2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
      anon_sym_STAR,
      anon_sym_POUND,
      anon_sym_TILDE,
      anon_sym_RPAREN,
      anon_sym_DASH,
      anon_sym_PLUS,
      anon_sym_SLASH,
      sym_currency,
  [1601] = 5,
    ACTIONS(327), 1,
      sym_currency,
    ACTIONS(323), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(325), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    ACTIONS(319), 3,
      aux_sym__skipped_lines_token2,
      anon_sym_LBRACE,
      anon_sym_AT,
    ACTIONS(321), 3,
      aux_sym_metadata_token1,
      anon_sym_LBRACE_LBRACE,
      anon_sym_AT_AT,
  [1623] = 2,
    ACTIONS(189), 3,
      aux_sym__skipped_lines_token2,
      anon_sym_LBRACE,
      anon_sym_AT,
    ACTIONS(191), 8,
      aux_sym_metadata_token1,
      anon_sym_LBRACE_LBRACE,
      anon_sym_STAR,
      anon_sym_AT_AT,
      anon_sym_DASH,
      anon_sym_PLUS,
      anon_sym_SLASH,
      sym_currency,
  [1639] = 2,
    ACTIONS(179), 3,
      aux_sym__skipped_lines_token2,
      anon_sym_LBRACE,
      anon_sym_AT,
    ACTIONS(181), 8,
      aux_sym_metadata_token1,
      anon_sym_LBRACE_LBRACE,
      anon_sym_STAR,
      anon_sym_AT_AT,
      anon_sym_DASH,
      anon_sym_PLUS,
      anon_sym_SLASH,
      sym_currency,
  [1655] = 2,
    ACTIONS(173), 3,
      aux_sym__skipped_lines_token2,
      anon_sym_LBRACE,
      anon_sym_AT,
    ACTIONS(175), 8,
      aux_sym_metadata_token1,
      anon_sym_LBRACE_LBRACE,
      anon_sym_STAR,
      anon_sym_AT_AT,
      anon_sym_DASH,
      anon_sym_PLUS,
      anon_sym_SLASH,
      sym_currency,
  [1671] = 3,
    ACTIONS(323), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(173), 3,
      aux_sym__skipped_lines_token2,
      anon_sym_LBRACE,
      anon_sym_AT,
    ACTIONS(175), 6,
      aux_sym_metadata_token1,
      anon_sym_LBRACE_LBRACE,
      anon_sym_AT_AT,
      anon_sym_DASH,
      anon_sym_PLUS,
      sym_currency,
  [1689] = 10,
    ACTIONS(71), 1,
      anon_sym_LBRACE,
    ACTIONS(73), 1,
      anon_sym_LBRACE_LBRACE,
    ACTIONS(75), 1,
      anon_sym_AT_AT,
    ACTIONS(77), 1,
      anon_sym_AT,
    ACTIONS(329), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(331), 1,
      aux_sym_metadata_token1,
    STATE(106), 1,
      sym_cost_spec,
    STATE(146), 1,
      sym_price_annotation,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(178), 1,
      sym_metadata,
  [1720] = 5,
    ACTIONS(128), 1,
      anon_sym_LPAREN,
    ACTIONS(334), 1,
      sym_number,
    ACTIONS(130), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(153), 2,
      sym_amount,
      sym_amount_with_tolerance,
    STATE(111), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1741] = 8,
    ACTIONS(313), 1,
      aux_sym_metadata_token1,
    STATE(116), 1,
      sym_tags_and_links,
    STATE(128), 1,
      aux_sym_tags_and_links_repeat1,
    STATE(147), 1,
      sym_metadata,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(239), 1,
      sym_postings,
    ACTIONS(315), 2,
      sym_tag,
      sym_link,
    STATE(149), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [1768] = 10,
    ACTIONS(71), 1,
      anon_sym_LBRACE,
    ACTIONS(73), 1,
      anon_sym_LBRACE_LBRACE,
    ACTIONS(75), 1,
      anon_sym_AT_AT,
    ACTIONS(77), 1,
      anon_sym_AT,
    ACTIONS(336), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(338), 1,
      aux_sym_metadata_token1,
    STATE(105), 1,
      sym_cost_spec,
    STATE(133), 1,
      sym_price_annotation,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(200), 1,
      sym_metadata,
  [1799] = 2,
    ACTIONS(341), 3,
      aux_sym__skipped_lines_token2,
      sym_bool,
      sym_number,
    ACTIONS(343), 7,
      aux_sym_metadata_token1,
      anon_sym_LPAREN,
      anon_sym_DASH,
      anon_sym_PLUS,
      sym_date,
      sym_string,
      sym_account,
  [1814] = 5,
    ACTIONS(128), 1,
      anon_sym_LPAREN,
    ACTIONS(345), 1,
      sym_currency,
    ACTIONS(347), 1,
      sym_number,
    ACTIONS(130), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(117), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1834] = 5,
    ACTIONS(128), 1,
      anon_sym_LPAREN,
    ACTIONS(349), 1,
      sym_number,
    STATE(163), 1,
      sym_amount,
    ACTIONS(130), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(119), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1854] = 6,
    ACTIONS(351), 1,
      anon_sym_RBRACE,
    ACTIONS(355), 1,
      anon_sym_POUND,
    ACTIONS(359), 1,
      sym_currency,
    ACTIONS(311), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(353), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
    ACTIONS(357), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [1876] = 5,
    ACTIONS(128), 1,
      anon_sym_LPAREN,
    ACTIONS(361), 1,
      sym_currency,
    ACTIONS(363), 1,
      sym_number,
    ACTIONS(130), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(123), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1896] = 4,
    ACTIONS(128), 1,
      anon_sym_LPAREN,
    ACTIONS(365), 1,
      sym_number,
    ACTIONS(130), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(124), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1913] = 4,
    ACTIONS(128), 1,
      anon_sym_LPAREN,
    ACTIONS(367), 1,
      sym_number,
    ACTIONS(130), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(127), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1930] = 4,
    ACTIONS(79), 1,
      anon_sym_LPAREN,
    ACTIONS(369), 1,
      sym_number,
    ACTIONS(81), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(80), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1947] = 4,
    ACTIONS(79), 1,
      anon_sym_LPAREN,
    ACTIONS(371), 1,
      sym_number,
    ACTIONS(81), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(79), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1964] = 4,
    ACTIONS(128), 1,
      anon_sym_LPAREN,
    ACTIONS(373), 1,
      sym_number,
    ACTIONS(130), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(72), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1981] = 4,
    ACTIONS(128), 1,
      anon_sym_LPAREN,
    ACTIONS(375), 1,
      sym_number,
    ACTIONS(130), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(69), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1998] = 4,
    ACTIONS(79), 1,
      anon_sym_LPAREN,
    ACTIONS(377), 1,
      sym_number,
    ACTIONS(81), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(77), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2015] = 7,
    ACTIONS(379), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(381), 1,
      aux_sym_metadata_token1,
    STATE(128), 1,
      aux_sym_tags_and_links_repeat1,
    STATE(134), 1,
      sym_tags_and_links,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(207), 1,
      sym_metadata,
    ACTIONS(315), 2,
      sym_tag,
      sym_link,
  [2038] = 4,
    ACTIONS(96), 1,
      anon_sym_LPAREN,
    ACTIONS(383), 1,
      sym_number,
    ACTIONS(98), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(20), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2055] = 4,
    ACTIONS(128), 1,
      anon_sym_LPAREN,
    ACTIONS(385), 1,
      sym_number,
    ACTIONS(130), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(75), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2072] = 4,
    ACTIONS(96), 1,
      anon_sym_LPAREN,
    ACTIONS(387), 1,
      sym_number,
    ACTIONS(98), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(21), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2089] = 4,
    ACTIONS(96), 1,
      anon_sym_LPAREN,
    ACTIONS(389), 1,
      sym_number,
    ACTIONS(98), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(26), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2106] = 4,
    ACTIONS(128), 1,
      anon_sym_LPAREN,
    ACTIONS(391), 1,
      sym_number,
    ACTIONS(130), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(130), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2123] = 4,
    ACTIONS(128), 1,
      anon_sym_LPAREN,
    ACTIONS(393), 1,
      sym_number,
    ACTIONS(130), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(129), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2140] = 7,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(395), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(397), 1,
      sym_string,
    ACTIONS(399), 1,
      sym_currency,
    STATE(120), 1,
      sym_currency_list,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(229), 1,
      sym_metadata,
  [2162] = 7,
    ACTIONS(75), 1,
      anon_sym_AT_AT,
    ACTIONS(77), 1,
      anon_sym_AT,
    ACTIONS(401), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(403), 1,
      aux_sym_metadata_token1,
    STATE(164), 1,
      sym_price_annotation,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(183), 1,
      sym_metadata,
  [2184] = 7,
    ACTIONS(75), 1,
      anon_sym_AT_AT,
    ACTIONS(77), 1,
      anon_sym_AT,
    ACTIONS(406), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(408), 1,
      aux_sym_metadata_token1,
    STATE(150), 1,
      sym_price_annotation,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(181), 1,
      sym_metadata,
  [2206] = 6,
    ACTIONS(411), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(413), 1,
      sym_key,
    ACTIONS(417), 1,
      sym_flag,
    ACTIONS(419), 1,
      sym_account,
    STATE(186), 1,
      sym_key_value,
    ACTIONS(415), 2,
      sym_tag,
      sym_link,
  [2226] = 5,
    ACTIONS(421), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(423), 1,
      aux_sym_metadata_token1,
    ACTIONS(425), 1,
      sym_currency,
    ACTIONS(323), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(325), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2244] = 7,
    ACTIONS(75), 1,
      anon_sym_AT_AT,
    ACTIONS(77), 1,
      anon_sym_AT,
    ACTIONS(427), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(429), 1,
      aux_sym_metadata_token1,
    STATE(140), 1,
      sym_price_annotation,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(189), 1,
      sym_metadata,
  [2266] = 7,
    ACTIONS(75), 1,
      anon_sym_AT_AT,
    ACTIONS(77), 1,
      anon_sym_AT,
    ACTIONS(432), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(434), 1,
      aux_sym_metadata_token1,
    STATE(135), 1,
      sym_price_annotation,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(198), 1,
      sym_metadata,
  [2288] = 4,
    ACTIONS(425), 1,
      sym_currency,
    ACTIONS(437), 1,
      anon_sym_TILDE,
    ACTIONS(311), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(357), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2303] = 5,
    ACTIONS(439), 1,
      aux_sym_metadata_token1,
    STATE(151), 1,
      sym_metadata,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(236), 1,
      sym_postings,
    STATE(149), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [2320] = 2,
    ACTIONS(441), 3,
      aux_sym__skipped_lines_token2,
      anon_sym_LBRACE,
      anon_sym_AT,
    ACTIONS(443), 3,
      aux_sym_metadata_token1,
      anon_sym_LBRACE_LBRACE,
      anon_sym_AT_AT,
  [2331] = 4,
    ACTIONS(423), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(445), 1,
      sym_currency,
    ACTIONS(311), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(357), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2346] = 2,
    ACTIONS(319), 3,
      aux_sym__skipped_lines_token2,
      anon_sym_LBRACE,
      anon_sym_AT,
    ACTIONS(321), 3,
      aux_sym_metadata_token1,
      anon_sym_LBRACE_LBRACE,
      anon_sym_AT_AT,
  [2357] = 5,
    ACTIONS(439), 1,
      aux_sym_metadata_token1,
    STATE(160), 1,
      sym_metadata,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(228), 1,
      sym_postings,
    STATE(149), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [2374] = 3,
    ACTIONS(447), 1,
      sym_currency,
    ACTIONS(311), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(357), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2386] = 4,
    ACTIONS(449), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(451), 1,
      aux_sym_metadata_token1,
    STATE(118), 1,
      aux_sym_tags_and_links_repeat1,
    ACTIONS(454), 2,
      sym_tag,
      sym_link,
  [2400] = 3,
    ACTIONS(425), 1,
      sym_currency,
    ACTIONS(311), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(357), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2412] = 5,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(457), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(459), 1,
      sym_string,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(238), 1,
      sym_metadata,
  [2428] = 4,
    ACTIONS(461), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(465), 1,
      anon_sym_COMMA,
    STATE(125), 1,
      aux_sym_currency_list_repeat1,
    ACTIONS(463), 2,
      aux_sym_metadata_token1,
      sym_string,
  [2442] = 4,
    ACTIONS(467), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(471), 1,
      anon_sym_COMMA,
    STATE(122), 1,
      aux_sym_currency_list_repeat1,
    ACTIONS(469), 2,
      aux_sym_metadata_token1,
      sym_string,
  [2456] = 3,
    ACTIONS(474), 1,
      sym_currency,
    ACTIONS(311), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(357), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2468] = 3,
    ACTIONS(476), 1,
      sym_currency,
    ACTIONS(311), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(357), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2480] = 4,
    ACTIONS(465), 1,
      anon_sym_COMMA,
    ACTIONS(478), 1,
      aux_sym__skipped_lines_token2,
    STATE(122), 1,
      aux_sym_currency_list_repeat1,
    ACTIONS(480), 2,
      aux_sym_metadata_token1,
      sym_string,
  [2494] = 5,
    ACTIONS(411), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(413), 1,
      sym_key,
    ACTIONS(417), 1,
      sym_flag,
    ACTIONS(419), 1,
      sym_account,
    STATE(186), 1,
      sym_key_value,
  [2510] = 3,
    ACTIONS(482), 1,
      anon_sym_RPAREN,
    ACTIONS(311), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(357), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2522] = 4,
    ACTIONS(484), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(486), 1,
      aux_sym_metadata_token1,
    STATE(118), 1,
      aux_sym_tags_and_links_repeat1,
    ACTIONS(489), 2,
      sym_tag,
      sym_link,
  [2536] = 3,
    ACTIONS(491), 1,
      anon_sym_RPAREN,
    ACTIONS(311), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(357), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2548] = 3,
    ACTIONS(493), 1,
      anon_sym_RPAREN,
    ACTIONS(311), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(357), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2560] = 3,
    ACTIONS(413), 1,
      sym_key,
    STATE(186), 1,
      sym_key_value,
    ACTIONS(415), 2,
      sym_tag,
      sym_link,
  [2571] = 4,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(495), 1,
      aux_sym__skipped_lines_token2,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(237), 1,
      sym_metadata,
  [2584] = 4,
    ACTIONS(497), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(499), 1,
      aux_sym_metadata_token1,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(188), 1,
      sym_metadata,
  [2597] = 4,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(502), 1,
      aux_sym__skipped_lines_token2,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(224), 1,
      sym_metadata,
  [2610] = 4,
    ACTIONS(504), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(506), 1,
      aux_sym_metadata_token1,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(195), 1,
      sym_metadata,
  [2623] = 4,
    ACTIONS(509), 1,
      anon_sym_RBRACE,
    ACTIONS(511), 1,
      anon_sym_RBRACE_RBRACE,
    ACTIONS(513), 1,
      anon_sym_COMMA,
    STATE(155), 1,
      aux_sym_cost_comp_list_repeat1,
  [2636] = 4,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(515), 1,
      aux_sym__skipped_lines_token2,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(222), 1,
      sym_metadata,
  [2649] = 2,
    ACTIONS(517), 2,
      aux_sym__skipped_lines_token2,
      anon_sym_AT,
    ACTIONS(519), 2,
      aux_sym_metadata_token1,
      anon_sym_AT_AT,
  [2658] = 4,
    ACTIONS(521), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(523), 1,
      aux_sym_metadata_token1,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(180), 1,
      sym_metadata,
  [2671] = 4,
    ACTIONS(526), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(528), 1,
      aux_sym_metadata_token1,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(191), 1,
      sym_metadata,
  [2684] = 2,
    ACTIONS(533), 1,
      sym_string,
    ACTIONS(531), 3,
      aux_sym_metadata_token1,
      sym_tag,
      sym_link,
  [2693] = 3,
    ACTIONS(535), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(537), 1,
      aux_sym_metadata_token1,
    STATE(142), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [2704] = 3,
    ACTIONS(540), 1,
      aux_sym_metadata_token1,
    STATE(233), 1,
      sym_postings,
    STATE(149), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [2715] = 4,
    ACTIONS(542), 1,
      anon_sym_RBRACE,
    ACTIONS(544), 1,
      anon_sym_RBRACE_RBRACE,
    ACTIONS(546), 1,
      anon_sym_COMMA,
    STATE(144), 1,
      aux_sym_cost_comp_list_repeat1,
  [2728] = 4,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(549), 1,
      aux_sym__skipped_lines_token2,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(219), 1,
      sym_metadata,
  [2741] = 4,
    ACTIONS(551), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(553), 1,
      aux_sym_metadata_token1,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(182), 1,
      sym_metadata,
  [2754] = 3,
    ACTIONS(540), 1,
      aux_sym_metadata_token1,
    STATE(230), 1,
      sym_postings,
    STATE(149), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [2765] = 4,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(556), 1,
      aux_sym__skipped_lines_token2,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(226), 1,
      sym_metadata,
  [2778] = 3,
    ACTIONS(540), 1,
      aux_sym_metadata_token1,
    ACTIONS(558), 1,
      aux_sym__skipped_lines_token2,
    STATE(142), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [2789] = 4,
    ACTIONS(560), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(562), 1,
      aux_sym_metadata_token1,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(179), 1,
      sym_metadata,
  [2802] = 3,
    ACTIONS(540), 1,
      aux_sym_metadata_token1,
    STATE(203), 1,
      sym_postings,
    STATE(149), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [2813] = 2,
    ACTIONS(467), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(469), 3,
      aux_sym_metadata_token1,
      anon_sym_COMMA,
      sym_string,
  [2822] = 4,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(565), 1,
      aux_sym__skipped_lines_token2,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(247), 1,
      sym_metadata,
  [2835] = 2,
    ACTIONS(567), 2,
      aux_sym__skipped_lines_token2,
      anon_sym_AT,
    ACTIONS(569), 2,
      aux_sym_metadata_token1,
      anon_sym_AT_AT,
  [2844] = 4,
    ACTIONS(513), 1,
      anon_sym_COMMA,
    ACTIONS(571), 1,
      anon_sym_RBRACE,
    ACTIONS(573), 1,
      anon_sym_RBRACE_RBRACE,
    STATE(144), 1,
      aux_sym_cost_comp_list_repeat1,
  [2857] = 4,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(575), 1,
      aux_sym__skipped_lines_token2,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(254), 1,
      sym_metadata,
  [2870] = 4,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(577), 1,
      aux_sym__skipped_lines_token2,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(245), 1,
      sym_metadata,
  [2883] = 4,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(579), 1,
      aux_sym__skipped_lines_token2,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(242), 1,
      sym_metadata,
  [2896] = 2,
    ACTIONS(449), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(581), 3,
      aux_sym_metadata_token1,
      sym_tag,
      sym_link,
  [2905] = 3,
    ACTIONS(540), 1,
      aux_sym_metadata_token1,
    STATE(209), 1,
      sym_postings,
    STATE(149), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [2916] = 4,
    ACTIONS(583), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(585), 1,
      aux_sym_metadata_token1,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(202), 1,
      sym_metadata,
  [2929] = 4,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(588), 1,
      aux_sym__skipped_lines_token2,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(234), 1,
      sym_metadata,
  [2942] = 4,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(590), 1,
      aux_sym__skipped_lines_token2,
    STATE(167), 1,
      aux_sym_metadata_repeat1,
    STATE(235), 1,
      sym_metadata,
  [2955] = 4,
    ACTIONS(592), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(594), 1,
      aux_sym_metadata_token1,
    STATE(177), 1,
      aux_sym_metadata_repeat1,
    STATE(190), 1,
      sym_metadata,
  [2968] = 2,
    ACTIONS(597), 1,
      anon_sym_RBRACE,
    ACTIONS(599), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [2976] = 3,
    ACTIONS(411), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(417), 1,
      sym_flag,
    ACTIONS(419), 1,
      sym_account,
  [2986] = 3,
    ACTIONS(94), 1,
      aux_sym_metadata_token1,
    ACTIONS(601), 1,
      aux_sym__skipped_lines_token2,
    STATE(172), 1,
      aux_sym_metadata_repeat1,
  [2996] = 2,
    ACTIONS(603), 1,
      anon_sym_RBRACE,
    ACTIONS(605), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [3004] = 2,
    ACTIONS(607), 1,
      anon_sym_RBRACE,
    ACTIONS(609), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [3012] = 2,
    ACTIONS(611), 1,
      anon_sym_RBRACE,
    ACTIONS(613), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [3020] = 2,
    ACTIONS(615), 1,
      anon_sym_RBRACE,
    ACTIONS(617), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [3028] = 3,
    ACTIONS(619), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(621), 1,
      aux_sym_metadata_token1,
    STATE(172), 1,
      aux_sym_metadata_repeat1,
  [3038] = 2,
    ACTIONS(624), 1,
      anon_sym_RBRACE,
    ACTIONS(626), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [3046] = 2,
    ACTIONS(542), 1,
      anon_sym_RBRACE,
    ACTIONS(544), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [3054] = 1,
    ACTIONS(628), 3,
      aux_sym_metadata_token1,
      sym_tag,
      sym_link,
  [3060] = 2,
    ACTIONS(630), 1,
      anon_sym_RBRACE,
    ACTIONS(632), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [3068] = 3,
    ACTIONS(601), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(634), 1,
      aux_sym_metadata_token1,
    STATE(172), 1,
      aux_sym_metadata_repeat1,
  [3078] = 2,
    ACTIONS(637), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(639), 1,
      aux_sym_metadata_token1,
  [3085] = 2,
    ACTIONS(641), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(643), 1,
      aux_sym_metadata_token1,
  [3092] = 2,
    ACTIONS(645), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(647), 1,
      aux_sym_metadata_token1,
  [3099] = 2,
    ACTIONS(649), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(651), 1,
      aux_sym_metadata_token1,
  [3106] = 2,
    ACTIONS(653), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(655), 1,
      aux_sym_metadata_token1,
  [3113] = 2,
    ACTIONS(657), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(659), 1,
      aux_sym_metadata_token1,
  [3120] = 1,
    ACTIONS(415), 2,
      sym_tag,
      sym_link,
  [3125] = 2,
    ACTIONS(413), 1,
      sym_key,
    STATE(186), 1,
      sym_key_value,
  [3132] = 2,
    ACTIONS(619), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(661), 1,
      aux_sym_metadata_token1,
  [3139] = 2,
    ACTIONS(663), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(665), 1,
      aux_sym_metadata_token1,
  [3146] = 2,
    ACTIONS(667), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(669), 1,
      aux_sym_metadata_token1,
  [3153] = 2,
    ACTIONS(671), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(673), 1,
      aux_sym_metadata_token1,
  [3160] = 2,
    ACTIONS(675), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(677), 1,
      aux_sym_metadata_token1,
  [3167] = 2,
    ACTIONS(679), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(681), 1,
      aux_sym_metadata_token1,
  [3174] = 2,
    ACTIONS(683), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(685), 1,
      aux_sym_metadata_token1,
  [3181] = 2,
    ACTIONS(687), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(689), 1,
      aux_sym_metadata_token1,
  [3188] = 2,
    ACTIONS(535), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(691), 1,
      aux_sym_metadata_token1,
  [3195] = 2,
    ACTIONS(693), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(695), 1,
      aux_sym_metadata_token1,
  [3202] = 2,
    ACTIONS(697), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(699), 1,
      aux_sym_metadata_token1,
  [3209] = 2,
    ACTIONS(701), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(703), 1,
      aux_sym_metadata_token1,
  [3216] = 2,
    ACTIONS(705), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(707), 1,
      aux_sym_metadata_token1,
  [3223] = 2,
    ACTIONS(709), 1,
      sym_key,
    STATE(251), 1,
      sym_key_value,
  [3230] = 2,
    ACTIONS(711), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(713), 1,
      aux_sym_metadata_token1,
  [3237] = 2,
    ACTIONS(715), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(717), 1,
      sym_string,
  [3244] = 2,
    ACTIONS(719), 1,
      aux_sym__skipped_lines_token2,
    ACTIONS(721), 1,
      aux_sym_metadata_token1,
  [3251] = 1,
    ACTIONS(723), 1,
      aux_sym__skipped_lines_token2,
  [3255] = 1,
    ACTIONS(725), 1,
      sym_string,
  [3259] = 1,
    ACTIONS(727), 1,
      anon_sym_RBRACE_RBRACE,
  [3263] = 1,
    ACTIONS(729), 1,
      sym_string,
  [3267] = 1,
    ACTIONS(731), 1,
      aux_sym__skipped_lines_token2,
  [3271] = 1,
    ACTIONS(699), 1,
      aux_sym__skipped_lines_token2,
  [3275] = 1,
    ACTIONS(733), 1,
      aux_sym__skipped_lines_token2,
  [3279] = 1,
    ACTIONS(735), 1,
      aux_sym__skipped_lines_token2,
  [3283] = 1,
    ACTIONS(727), 1,
      anon_sym_RBRACE,
  [3287] = 1,
    ACTIONS(737), 1,
      aux_sym__skipped_lines_token2,
  [3291] = 1,
    ACTIONS(739), 1,
      sym_string,
  [3295] = 1,
    ACTIONS(741), 1,
      sym_string,
  [3299] = 1,
    ACTIONS(743), 1,
      sym_account,
  [3303] = 1,
    ACTIONS(745), 1,
      sym_string,
  [3307] = 1,
    ACTIONS(747), 1,
      sym_currency,
  [3311] = 1,
    ACTIONS(749), 1,
      aux_sym__skipped_lines_token2,
  [3315] = 1,
    ACTIONS(751), 1,
      aux_sym__skipped_lines_token2,
  [3319] = 1,
    ACTIONS(343), 1,
      aux_sym__skipped_lines_token2,
  [3323] = 1,
    ACTIONS(753), 1,
      sym_account,
  [3327] = 1,
    ACTIONS(755), 1,
      aux_sym__skipped_lines_token2,
  [3331] = 1,
    ACTIONS(757), 1,
      sym_account,
  [3335] = 1,
    ACTIONS(759), 1,
      aux_sym__skipped_lines_token2,
  [3339] = 1,
    ACTIONS(761), 1,
      sym_account,
  [3343] = 1,
    ACTIONS(763), 1,
      aux_sym__skipped_lines_token2,
  [3347] = 1,
    ACTIONS(765), 1,
      aux_sym__skipped_lines_token2,
  [3351] = 1,
    ACTIONS(767), 1,
      aux_sym__skipped_lines_token2,
  [3355] = 1,
    ACTIONS(769), 1,
      aux_sym__skipped_lines_token2,
  [3359] = 1,
    ACTIONS(771), 1,
      aux_sym__skipped_lines_token2,
  [3363] = 1,
    ACTIONS(773), 1,
      sym_string,
  [3367] = 1,
    ACTIONS(775), 1,
      sym_account,
  [3371] = 1,
    ACTIONS(777), 1,
      aux_sym__skipped_lines_token2,
  [3375] = 1,
    ACTIONS(779), 1,
      aux_sym__skipped_lines_token2,
  [3379] = 1,
    ACTIONS(781), 1,
      aux_sym__skipped_lines_token2,
  [3383] = 1,
    ACTIONS(783), 1,
      aux_sym__skipped_lines_token2,
  [3387] = 1,
    ACTIONS(785), 1,
      aux_sym__skipped_lines_token2,
  [3391] = 1,
    ACTIONS(787), 1,
      aux_sym__skipped_lines_token2,
  [3395] = 1,
    ACTIONS(789), 1,
      aux_sym__skipped_lines_token2,
  [3399] = 1,
    ACTIONS(791), 1,
      sym_account,
  [3403] = 1,
    ACTIONS(793), 1,
      sym_currency,
  [3407] = 1,
    ACTIONS(795), 1,
      aux_sym__skipped_lines_token2,
  [3411] = 1,
    ACTIONS(797), 1,
      aux_sym__skipped_lines_token1,
  [3415] = 1,
    ACTIONS(799), 1,
      sym_string,
  [3419] = 1,
    ACTIONS(801), 1,
      aux_sym__skipped_lines_token2,
  [3423] = 1,
    ACTIONS(803), 1,
      sym_currency,
  [3427] = 1,
    ACTIONS(805), 1,
      aux_sym__skipped_lines_token2,
  [3431] = 1,
    ACTIONS(807), 1,
      sym_account,
  [3435] = 1,
    ACTIONS(809), 1,
      sym_account,
  [3439] = 1,
    ACTIONS(811), 1,
      aux_sym__skipped_lines_token2,
  [3443] = 1,
    ACTIONS(813), 1,
      aux_sym__skipped_lines_token2,
  [3447] = 1,
    ACTIONS(815), 1,
      aux_sym__skipped_lines_token2,
  [3451] = 1,
    ACTIONS(817), 1,
      aux_sym__skipped_lines_token2,
  [3455] = 1,
    ACTIONS(819), 1,
      aux_sym__skipped_lines_token2,
  [3459] = 1,
    ACTIONS(821), 1,
      sym_string,
  [3463] = 1,
    ACTIONS(823), 1,
      aux_sym__skipped_lines_token2,
  [3467] = 1,
    ACTIONS(825), 1,
      aux_sym__skipped_lines_token2,
  [3471] = 1,
    ACTIONS(827), 1,
      ts_builtin_sym_end,
  [3475] = 1,
    ACTIONS(829), 1,
      sym_key,
  [3479] = 1,
    ACTIONS(831), 1,
      aux_sym__skipped_lines_token2,
  [3483] = 1,
    ACTIONS(833), 1,
      sym_tag,
  [3487] = 1,
    ACTIONS(835), 1,
      sym_tag,
  [3491] = 1,
    ACTIONS(837), 1,
      sym_string,
  [3495] = 1,
    ACTIONS(839), 1,
      sym_string,
  [3499] = 1,
    ACTIONS(841), 1,
      sym_string,
  [3503] = 1,
    ACTIONS(843), 1,
      aux_sym__skipped_lines_token2,
};

static uint32_t ts_small_parse_table_map[] = {
  [SMALL_STATE(2)] = 0,
  [SMALL_STATE(3)] = 63,
  [SMALL_STATE(4)] = 126,
  [SMALL_STATE(5)] = 179,
  [SMALL_STATE(6)] = 232,
  [SMALL_STATE(7)] = 273,
  [SMALL_STATE(8)] = 314,
  [SMALL_STATE(9)] = 351,
  [SMALL_STATE(10)] = 391,
  [SMALL_STATE(11)] = 431,
  [SMALL_STATE(12)] = 465,
  [SMALL_STATE(13)] = 500,
  [SMALL_STATE(14)] = 534,
  [SMALL_STATE(15)] = 550,
  [SMALL_STATE(16)] = 566,
  [SMALL_STATE(17)] = 582,
  [SMALL_STATE(18)] = 598,
  [SMALL_STATE(19)] = 614,
  [SMALL_STATE(20)] = 630,
  [SMALL_STATE(21)] = 650,
  [SMALL_STATE(22)] = 668,
  [SMALL_STATE(23)] = 686,
  [SMALL_STATE(24)] = 702,
  [SMALL_STATE(25)] = 718,
  [SMALL_STATE(26)] = 734,
  [SMALL_STATE(27)] = 752,
  [SMALL_STATE(28)] = 768,
  [SMALL_STATE(29)] = 784,
  [SMALL_STATE(30)] = 800,
  [SMALL_STATE(31)] = 816,
  [SMALL_STATE(32)] = 832,
  [SMALL_STATE(33)] = 848,
  [SMALL_STATE(34)] = 864,
  [SMALL_STATE(35)] = 880,
  [SMALL_STATE(36)] = 896,
  [SMALL_STATE(37)] = 912,
  [SMALL_STATE(38)] = 928,
  [SMALL_STATE(39)] = 944,
  [SMALL_STATE(40)] = 960,
  [SMALL_STATE(41)] = 976,
  [SMALL_STATE(42)] = 992,
  [SMALL_STATE(43)] = 1008,
  [SMALL_STATE(44)] = 1024,
  [SMALL_STATE(45)] = 1040,
  [SMALL_STATE(46)] = 1056,
  [SMALL_STATE(47)] = 1072,
  [SMALL_STATE(48)] = 1088,
  [SMALL_STATE(49)] = 1104,
  [SMALL_STATE(50)] = 1120,
  [SMALL_STATE(51)] = 1136,
  [SMALL_STATE(52)] = 1152,
  [SMALL_STATE(53)] = 1168,
  [SMALL_STATE(54)] = 1184,
  [SMALL_STATE(55)] = 1200,
  [SMALL_STATE(56)] = 1216,
  [SMALL_STATE(57)] = 1232,
  [SMALL_STATE(58)] = 1248,
  [SMALL_STATE(59)] = 1264,
  [SMALL_STATE(60)] = 1288,
  [SMALL_STATE(61)] = 1304,
  [SMALL_STATE(62)] = 1320,
  [SMALL_STATE(63)] = 1336,
  [SMALL_STATE(64)] = 1352,
  [SMALL_STATE(65)] = 1368,
  [SMALL_STATE(66)] = 1384,
  [SMALL_STATE(67)] = 1400,
  [SMALL_STATE(68)] = 1416,
  [SMALL_STATE(69)] = 1432,
  [SMALL_STATE(70)] = 1449,
  [SMALL_STATE(71)] = 1478,
  [SMALL_STATE(72)] = 1515,
  [SMALL_STATE(73)] = 1534,
  [SMALL_STATE(74)] = 1567,
  [SMALL_STATE(75)] = 1584,
  [SMALL_STATE(76)] = 1601,
  [SMALL_STATE(77)] = 1623,
  [SMALL_STATE(78)] = 1639,
  [SMALL_STATE(79)] = 1655,
  [SMALL_STATE(80)] = 1671,
  [SMALL_STATE(81)] = 1689,
  [SMALL_STATE(82)] = 1720,
  [SMALL_STATE(83)] = 1741,
  [SMALL_STATE(84)] = 1768,
  [SMALL_STATE(85)] = 1799,
  [SMALL_STATE(86)] = 1814,
  [SMALL_STATE(87)] = 1834,
  [SMALL_STATE(88)] = 1854,
  [SMALL_STATE(89)] = 1876,
  [SMALL_STATE(90)] = 1896,
  [SMALL_STATE(91)] = 1913,
  [SMALL_STATE(92)] = 1930,
  [SMALL_STATE(93)] = 1947,
  [SMALL_STATE(94)] = 1964,
  [SMALL_STATE(95)] = 1981,
  [SMALL_STATE(96)] = 1998,
  [SMALL_STATE(97)] = 2015,
  [SMALL_STATE(98)] = 2038,
  [SMALL_STATE(99)] = 2055,
  [SMALL_STATE(100)] = 2072,
  [SMALL_STATE(101)] = 2089,
  [SMALL_STATE(102)] = 2106,
  [SMALL_STATE(103)] = 2123,
  [SMALL_STATE(104)] = 2140,
  [SMALL_STATE(105)] = 2162,
  [SMALL_STATE(106)] = 2184,
  [SMALL_STATE(107)] = 2206,
  [SMALL_STATE(108)] = 2226,
  [SMALL_STATE(109)] = 2244,
  [SMALL_STATE(110)] = 2266,
  [SMALL_STATE(111)] = 2288,
  [SMALL_STATE(112)] = 2303,
  [SMALL_STATE(113)] = 2320,
  [SMALL_STATE(114)] = 2331,
  [SMALL_STATE(115)] = 2346,
  [SMALL_STATE(116)] = 2357,
  [SMALL_STATE(117)] = 2374,
  [SMALL_STATE(118)] = 2386,
  [SMALL_STATE(119)] = 2400,
  [SMALL_STATE(120)] = 2412,
  [SMALL_STATE(121)] = 2428,
  [SMALL_STATE(122)] = 2442,
  [SMALL_STATE(123)] = 2456,
  [SMALL_STATE(124)] = 2468,
  [SMALL_STATE(125)] = 2480,
  [SMALL_STATE(126)] = 2494,
  [SMALL_STATE(127)] = 2510,
  [SMALL_STATE(128)] = 2522,
  [SMALL_STATE(129)] = 2536,
  [SMALL_STATE(130)] = 2548,
  [SMALL_STATE(131)] = 2560,
  [SMALL_STATE(132)] = 2571,
  [SMALL_STATE(133)] = 2584,
  [SMALL_STATE(134)] = 2597,
  [SMALL_STATE(135)] = 2610,
  [SMALL_STATE(136)] = 2623,
  [SMALL_STATE(137)] = 2636,
  [SMALL_STATE(138)] = 2649,
  [SMALL_STATE(139)] = 2658,
  [SMALL_STATE(140)] = 2671,
  [SMALL_STATE(141)] = 2684,
  [SMALL_STATE(142)] = 2693,
  [SMALL_STATE(143)] = 2704,
  [SMALL_STATE(144)] = 2715,
  [SMALL_STATE(145)] = 2728,
  [SMALL_STATE(146)] = 2741,
  [SMALL_STATE(147)] = 2754,
  [SMALL_STATE(148)] = 2765,
  [SMALL_STATE(149)] = 2778,
  [SMALL_STATE(150)] = 2789,
  [SMALL_STATE(151)] = 2802,
  [SMALL_STATE(152)] = 2813,
  [SMALL_STATE(153)] = 2822,
  [SMALL_STATE(154)] = 2835,
  [SMALL_STATE(155)] = 2844,
  [SMALL_STATE(156)] = 2857,
  [SMALL_STATE(157)] = 2870,
  [SMALL_STATE(158)] = 2883,
  [SMALL_STATE(159)] = 2896,
  [SMALL_STATE(160)] = 2905,
  [SMALL_STATE(161)] = 2916,
  [SMALL_STATE(162)] = 2929,
  [SMALL_STATE(163)] = 2942,
  [SMALL_STATE(164)] = 2955,
  [SMALL_STATE(165)] = 2968,
  [SMALL_STATE(166)] = 2976,
  [SMALL_STATE(167)] = 2986,
  [SMALL_STATE(168)] = 2996,
  [SMALL_STATE(169)] = 3004,
  [SMALL_STATE(170)] = 3012,
  [SMALL_STATE(171)] = 3020,
  [SMALL_STATE(172)] = 3028,
  [SMALL_STATE(173)] = 3038,
  [SMALL_STATE(174)] = 3046,
  [SMALL_STATE(175)] = 3054,
  [SMALL_STATE(176)] = 3060,
  [SMALL_STATE(177)] = 3068,
  [SMALL_STATE(178)] = 3078,
  [SMALL_STATE(179)] = 3085,
  [SMALL_STATE(180)] = 3092,
  [SMALL_STATE(181)] = 3099,
  [SMALL_STATE(182)] = 3106,
  [SMALL_STATE(183)] = 3113,
  [SMALL_STATE(184)] = 3120,
  [SMALL_STATE(185)] = 3125,
  [SMALL_STATE(186)] = 3132,
  [SMALL_STATE(187)] = 3139,
  [SMALL_STATE(188)] = 3146,
  [SMALL_STATE(189)] = 3153,
  [SMALL_STATE(190)] = 3160,
  [SMALL_STATE(191)] = 3167,
  [SMALL_STATE(192)] = 3174,
  [SMALL_STATE(193)] = 3181,
  [SMALL_STATE(194)] = 3188,
  [SMALL_STATE(195)] = 3195,
  [SMALL_STATE(196)] = 3202,
  [SMALL_STATE(197)] = 3209,
  [SMALL_STATE(198)] = 3216,
  [SMALL_STATE(199)] = 3223,
  [SMALL_STATE(200)] = 3230,
  [SMALL_STATE(201)] = 3237,
  [SMALL_STATE(202)] = 3244,
  [SMALL_STATE(203)] = 3251,
  [SMALL_STATE(204)] = 3255,
  [SMALL_STATE(205)] = 3259,
  [SMALL_STATE(206)] = 3263,
  [SMALL_STATE(207)] = 3267,
  [SMALL_STATE(208)] = 3271,
  [SMALL_STATE(209)] = 3275,
  [SMALL_STATE(210)] = 3279,
  [SMALL_STATE(211)] = 3283,
  [SMALL_STATE(212)] = 3287,
  [SMALL_STATE(213)] = 3291,
  [SMALL_STATE(214)] = 3295,
  [SMALL_STATE(215)] = 3299,
  [SMALL_STATE(216)] = 3303,
  [SMALL_STATE(217)] = 3307,
  [SMALL_STATE(218)] = 3311,
  [SMALL_STATE(219)] = 3315,
  [SMALL_STATE(220)] = 3319,
  [SMALL_STATE(221)] = 3323,
  [SMALL_STATE(222)] = 3327,
  [SMALL_STATE(223)] = 3331,
  [SMALL_STATE(224)] = 3335,
  [SMALL_STATE(225)] = 3339,
  [SMALL_STATE(226)] = 3343,
  [SMALL_STATE(227)] = 3347,
  [SMALL_STATE(228)] = 3351,
  [SMALL_STATE(229)] = 3355,
  [SMALL_STATE(230)] = 3359,
  [SMALL_STATE(231)] = 3363,
  [SMALL_STATE(232)] = 3367,
  [SMALL_STATE(233)] = 3371,
  [SMALL_STATE(234)] = 3375,
  [SMALL_STATE(235)] = 3379,
  [SMALL_STATE(236)] = 3383,
  [SMALL_STATE(237)] = 3387,
  [SMALL_STATE(238)] = 3391,
  [SMALL_STATE(239)] = 3395,
  [SMALL_STATE(240)] = 3399,
  [SMALL_STATE(241)] = 3403,
  [SMALL_STATE(242)] = 3407,
  [SMALL_STATE(243)] = 3411,
  [SMALL_STATE(244)] = 3415,
  [SMALL_STATE(245)] = 3419,
  [SMALL_STATE(246)] = 3423,
  [SMALL_STATE(247)] = 3427,
  [SMALL_STATE(248)] = 3431,
  [SMALL_STATE(249)] = 3435,
  [SMALL_STATE(250)] = 3439,
  [SMALL_STATE(251)] = 3443,
  [SMALL_STATE(252)] = 3447,
  [SMALL_STATE(253)] = 3451,
  [SMALL_STATE(254)] = 3455,
  [SMALL_STATE(255)] = 3459,
  [SMALL_STATE(256)] = 3463,
  [SMALL_STATE(257)] = 3467,
  [SMALL_STATE(258)] = 3471,
  [SMALL_STATE(259)] = 3475,
  [SMALL_STATE(260)] = 3479,
  [SMALL_STATE(261)] = 3483,
  [SMALL_STATE(262)] = 3487,
  [SMALL_STATE(263)] = 3491,
  [SMALL_STATE(264)] = 3495,
  [SMALL_STATE(265)] = 3499,
  [SMALL_STATE(266)] = 3503,
};

static TSParseActionEntry ts_parse_actions[] = {
  [0] = {.count = 0, .reusable = false},
  [1] = {.count = 1, .reusable = false}, RECOVER(),
  [3] = {.count = 1, .reusable = true}, REDUCE(sym_beancount_file, 0),
  [5] = {.count = 1, .reusable = true}, SHIFT(3),
  [7] = {.count = 1, .reusable = true}, SHIFT(243),
  [9] = {.count = 1, .reusable = true}, SHIFT(266),
  [11] = {.count = 1, .reusable = true}, SHIFT(265),
  [13] = {.count = 1, .reusable = true}, SHIFT(264),
  [15] = {.count = 1, .reusable = true}, SHIFT(263),
  [17] = {.count = 1, .reusable = true}, SHIFT(262),
  [19] = {.count = 1, .reusable = true}, SHIFT(261),
  [21] = {.count = 1, .reusable = true}, SHIFT(199),
  [23] = {.count = 1, .reusable = true}, SHIFT(259),
  [25] = {.count = 1, .reusable = true}, SHIFT(71),
  [27] = {.count = 1, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2),
  [29] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(2),
  [32] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(243),
  [35] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(266),
  [38] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(265),
  [41] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(264),
  [44] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(263),
  [47] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(262),
  [50] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(261),
  [53] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(199),
  [56] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(259),
  [59] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(71),
  [62] = {.count = 1, .reusable = true}, REDUCE(sym_beancount_file, 1),
  [64] = {.count = 1, .reusable = true}, SHIFT(2),
  [66] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 2, .production_id = 10),
  [68] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 2, .production_id = 10), SHIFT(185),
  [71] = {.count = 1, .reusable = false}, SHIFT(10),
  [73] = {.count = 1, .reusable = true}, SHIFT(9),
  [75] = {.count = 1, .reusable = true}, SHIFT(70),
  [77] = {.count = 1, .reusable = false}, SHIFT(70),
  [79] = {.count = 1, .reusable = true}, SHIFT(103),
  [81] = {.count = 1, .reusable = true}, SHIFT(96),
  [83] = {.count = 1, .reusable = true}, SHIFT(115),
  [85] = {.count = 1, .reusable = true}, SHIFT(76),
  [87] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 3, .production_id = 24),
  [89] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 3, .production_id = 24), SHIFT(185),
  [92] = {.count = 1, .reusable = false}, SHIFT(32),
  [94] = {.count = 1, .reusable = true}, SHIFT(185),
  [96] = {.count = 1, .reusable = true}, SHIFT(91),
  [98] = {.count = 1, .reusable = true}, SHIFT(101),
  [100] = {.count = 1, .reusable = false}, SHIFT(12),
  [102] = {.count = 1, .reusable = true}, SHIFT(12),
  [104] = {.count = 1, .reusable = false}, SHIFT(59),
  [106] = {.count = 1, .reusable = false}, SHIFT(65),
  [108] = {.count = 1, .reusable = false}, SHIFT(6),
  [110] = {.count = 1, .reusable = true}, SHIFT(6),
  [112] = {.count = 1, .reusable = false}, REDUCE(sym_key_value, 1),
  [114] = {.count = 1, .reusable = true}, REDUCE(sym_key_value, 1),
  [116] = {.count = 1, .reusable = false}, SHIFT(196),
  [118] = {.count = 1, .reusable = true}, SHIFT(196),
  [120] = {.count = 1, .reusable = false}, SHIFT(108),
  [122] = {.count = 1, .reusable = true}, SHIFT(138),
  [124] = {.count = 1, .reusable = true}, SHIFT(170),
  [126] = {.count = 1, .reusable = true}, SHIFT(89),
  [128] = {.count = 1, .reusable = true}, SHIFT(102),
  [130] = {.count = 1, .reusable = true}, SHIFT(95),
  [132] = {.count = 1, .reusable = true}, SHIFT(169),
  [134] = {.count = 1, .reusable = false}, SHIFT(88),
  [136] = {.count = 1, .reusable = false}, SHIFT(208),
  [138] = {.count = 1, .reusable = true}, SHIFT(208),
  [140] = {.count = 1, .reusable = false}, SHIFT(114),
  [142] = {.count = 1, .reusable = false}, REDUCE(aux_sym_custom_repeat1, 2),
  [144] = {.count = 1, .reusable = true}, REDUCE(aux_sym_custom_repeat1, 2),
  [146] = {.count = 2, .reusable = true}, REDUCE(aux_sym_custom_repeat1, 2), SHIFT_REPEAT(91),
  [149] = {.count = 2, .reusable = true}, REDUCE(aux_sym_custom_repeat1, 2), SHIFT_REPEAT(101),
  [152] = {.count = 2, .reusable = false}, REDUCE(aux_sym_custom_repeat1, 2), SHIFT_REPEAT(12),
  [155] = {.count = 2, .reusable = true}, REDUCE(aux_sym_custom_repeat1, 2), SHIFT_REPEAT(12),
  [158] = {.count = 2, .reusable = false}, REDUCE(aux_sym_custom_repeat1, 2), SHIFT_REPEAT(59),
  [161] = {.count = 1, .reusable = true}, REDUCE(sym_include, 3),
  [163] = {.count = 1, .reusable = true}, REDUCE(sym_event, 5, .production_id = 17),
  [165] = {.count = 1, .reusable = true}, REDUCE(sym_commodity, 4, .production_id = 8),
  [167] = {.count = 1, .reusable = true}, REDUCE(sym_document, 6, .production_id = 35),
  [169] = {.count = 1, .reusable = true}, REDUCE(sym__skipped_lines, 2),
  [171] = {.count = 1, .reusable = true}, REDUCE(sym_note, 5, .production_id = 18),
  [173] = {.count = 1, .reusable = false}, REDUCE(sym_binary_num_expr, 3),
  [175] = {.count = 1, .reusable = true}, REDUCE(sym_binary_num_expr, 3),
  [177] = {.count = 1, .reusable = true}, SHIFT(100),
  [179] = {.count = 1, .reusable = false}, REDUCE(sym__paren_num_expr, 3),
  [181] = {.count = 1, .reusable = true}, REDUCE(sym__paren_num_expr, 3),
  [183] = {.count = 1, .reusable = true}, REDUCE(sym_open, 5, .production_id = 19),
  [185] = {.count = 1, .reusable = true}, REDUCE(sym_open, 5, .production_id = 13),
  [187] = {.count = 1, .reusable = true}, REDUCE(sym_open, 5, .production_id = 20),
  [189] = {.count = 1, .reusable = false}, REDUCE(sym_unary_num_expr, 2),
  [191] = {.count = 1, .reusable = true}, REDUCE(sym_unary_num_expr, 2),
  [193] = {.count = 1, .reusable = true}, REDUCE(sym_pad, 5, .production_id = 21),
  [195] = {.count = 1, .reusable = true}, REDUCE(sym_price, 5, .production_id = 22),
  [197] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 7, .production_id = 73),
  [199] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 4, .production_id = 11),
  [201] = {.count = 1, .reusable = true}, REDUCE(sym_query, 5, .production_id = 23),
  [203] = {.count = 1, .reusable = true}, REDUCE(sym_custom, 5, .production_id = 9),
  [205] = {.count = 1, .reusable = true}, REDUCE(sym_open, 7, .production_id = 60),
  [207] = {.count = 1, .reusable = true}, REDUCE(sym_document, 7, .production_id = 59),
  [209] = {.count = 1, .reusable = true}, REDUCE(sym_event, 6, .production_id = 36),
  [211] = {.count = 1, .reusable = true}, REDUCE(sym_close, 4, .production_id = 7),
  [213] = {.count = 1, .reusable = true}, REDUCE(sym__skipped_lines, 3),
  [215] = {.count = 1, .reusable = true}, REDUCE(sym_document, 6, .production_id = 34),
  [217] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 6, .production_id = 58),
  [219] = {.count = 1, .reusable = true}, REDUCE(sym_plugin, 3, .production_id = 1),
  [221] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 6, .production_id = 57),
  [223] = {.count = 1, .reusable = true}, REDUCE(sym_pushtag, 3, .production_id = 2),
  [225] = {.count = 1, .reusable = true}, REDUCE(sym_poptag, 3, .production_id = 2),
  [227] = {.count = 1, .reusable = true}, REDUCE(sym_balance, 5, .production_id = 12),
  [229] = {.count = 1, .reusable = true}, REDUCE(sym_note, 6, .production_id = 37),
  [231] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 6, .production_id = 56),
  [233] = {.count = 1, .reusable = true}, REDUCE(sym_close, 5, .production_id = 13),
  [235] = {.count = 1, .reusable = true}, REDUCE(sym_pushmeta, 3, .production_id = 3),
  [237] = {.count = 1, .reusable = true}, REDUCE(sym_popmeta, 3, .production_id = 4),
  [239] = {.count = 1, .reusable = true}, REDUCE(sym_open, 6, .production_id = 38),
  [241] = {.count = 1, .reusable = true}, REDUCE(sym_document, 5, .production_id = 16),
  [243] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 5, .production_id = 29),
  [245] = {.count = 1, .reusable = true}, REDUCE(sym_commodity, 5, .production_id = 14),
  [247] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 5, .production_id = 30),
  [249] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 5, .production_id = 31),
  [251] = {.count = 1, .reusable = true}, REDUCE(sym_open, 4, .production_id = 7),
  [253] = {.count = 1, .reusable = true}, REDUCE(sym_balance, 6, .production_id = 32),
  [255] = {.count = 1, .reusable = true}, REDUCE(sym_custom, 5, .production_id = 15),
  [257] = {.count = 1, .reusable = false}, REDUCE(aux_sym_custom_repeat1, 1),
  [259] = {.count = 1, .reusable = true}, REDUCE(aux_sym_custom_repeat1, 1),
  [261] = {.count = 1, .reusable = true}, SHIFT(98),
  [263] = {.count = 1, .reusable = false}, SHIFT(85),
  [265] = {.count = 1, .reusable = true}, REDUCE(sym_query, 6, .production_id = 43),
  [267] = {.count = 1, .reusable = true}, REDUCE(sym_custom, 6, .production_id = 33),
  [269] = {.count = 1, .reusable = true}, REDUCE(sym_price, 6, .production_id = 42),
  [271] = {.count = 1, .reusable = true}, REDUCE(sym_pad, 6, .production_id = 41),
  [273] = {.count = 1, .reusable = true}, REDUCE(sym_open, 6, .production_id = 40),
  [275] = {.count = 1, .reusable = true}, REDUCE(sym_custom, 4, .production_id = 9),
  [277] = {.count = 1, .reusable = true}, REDUCE(sym_open, 6, .production_id = 39),
  [279] = {.count = 1, .reusable = true}, REDUCE(sym_option, 4, .production_id = 5),
  [281] = {.count = 1, .reusable = true}, REDUCE(sym_plugin, 4, .production_id = 6),
  [283] = {.count = 1, .reusable = false}, REDUCE(sym_price_annotation, 1),
  [285] = {.count = 1, .reusable = true}, REDUCE(sym_price_annotation, 1),
  [287] = {.count = 1, .reusable = true}, SHIFT(249),
  [289] = {.count = 1, .reusable = true}, SHIFT(248),
  [291] = {.count = 1, .reusable = true}, SHIFT(246),
  [293] = {.count = 1, .reusable = true}, SHIFT(244),
  [295] = {.count = 1, .reusable = true}, SHIFT(240),
  [297] = {.count = 1, .reusable = true}, SHIFT(231),
  [299] = {.count = 1, .reusable = true}, SHIFT(225),
  [301] = {.count = 1, .reusable = true}, SHIFT(223),
  [303] = {.count = 1, .reusable = true}, SHIFT(221),
  [305] = {.count = 1, .reusable = true}, SHIFT(217),
  [307] = {.count = 1, .reusable = true}, SHIFT(213),
  [309] = {.count = 1, .reusable = true}, SHIFT(73),
  [311] = {.count = 1, .reusable = true}, SHIFT(99),
  [313] = {.count = 1, .reusable = true}, SHIFT(107),
  [315] = {.count = 1, .reusable = true}, SHIFT(128),
  [317] = {.count = 1, .reusable = true}, SHIFT(141),
  [319] = {.count = 1, .reusable = false}, REDUCE(sym_incomplete_amount, 1),
  [321] = {.count = 1, .reusable = true}, REDUCE(sym_incomplete_amount, 1),
  [323] = {.count = 1, .reusable = true}, SHIFT(93),
  [325] = {.count = 1, .reusable = true}, SHIFT(92),
  [327] = {.count = 1, .reusable = true}, SHIFT(113),
  [329] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 46),
  [331] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 46), SHIFT(185),
  [334] = {.count = 1, .reusable = true}, SHIFT(111),
  [336] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 3, .production_id = 27),
  [338] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 3, .production_id = 27), SHIFT(185),
  [341] = {.count = 1, .reusable = false}, REDUCE(sym_amount, 2),
  [343] = {.count = 1, .reusable = true}, REDUCE(sym_amount, 2),
  [345] = {.count = 1, .reusable = true}, SHIFT(171),
  [347] = {.count = 1, .reusable = true}, SHIFT(117),
  [349] = {.count = 1, .reusable = true}, SHIFT(119),
  [351] = {.count = 1, .reusable = false}, REDUCE(sym_compound_amount, 1, .production_id = 49),
  [353] = {.count = 1, .reusable = true}, REDUCE(sym_compound_amount, 1, .production_id = 49),
  [355] = {.count = 1, .reusable = true}, SHIFT(86),
  [357] = {.count = 1, .reusable = true}, SHIFT(94),
  [359] = {.count = 1, .reusable = true}, SHIFT(173),
  [361] = {.count = 1, .reusable = true}, SHIFT(176),
  [363] = {.count = 1, .reusable = true}, SHIFT(123),
  [365] = {.count = 1, .reusable = true}, SHIFT(124),
  [367] = {.count = 1, .reusable = true}, SHIFT(127),
  [369] = {.count = 1, .reusable = true}, SHIFT(80),
  [371] = {.count = 1, .reusable = true}, SHIFT(79),
  [373] = {.count = 1, .reusable = true}, SHIFT(72),
  [375] = {.count = 1, .reusable = true}, SHIFT(69),
  [377] = {.count = 1, .reusable = true}, SHIFT(77),
  [379] = {.count = 1, .reusable = false}, SHIFT(51),
  [381] = {.count = 1, .reusable = true}, SHIFT(131),
  [383] = {.count = 1, .reusable = true}, SHIFT(20),
  [385] = {.count = 1, .reusable = true}, SHIFT(75),
  [387] = {.count = 1, .reusable = true}, SHIFT(21),
  [389] = {.count = 1, .reusable = true}, SHIFT(26),
  [391] = {.count = 1, .reusable = true}, SHIFT(130),
  [393] = {.count = 1, .reusable = true}, SHIFT(129),
  [395] = {.count = 1, .reusable = false}, SHIFT(56),
  [397] = {.count = 1, .reusable = true}, SHIFT(158),
  [399] = {.count = 1, .reusable = true}, SHIFT(121),
  [401] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 53),
  [403] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 53), SHIFT(185),
  [406] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 64),
  [408] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 64), SHIFT(185),
  [411] = {.count = 1, .reusable = true}, SHIFT(194),
  [413] = {.count = 1, .reusable = true}, SHIFT(8),
  [415] = {.count = 1, .reusable = true}, SHIFT(159),
  [417] = {.count = 1, .reusable = false}, SHIFT(232),
  [419] = {.count = 1, .reusable = true}, SHIFT(4),
  [421] = {.count = 1, .reusable = false}, REDUCE(sym__key_value_value, 1),
  [423] = {.count = 1, .reusable = true}, REDUCE(sym__key_value_value, 1),
  [425] = {.count = 1, .reusable = true}, SHIFT(85),
  [427] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 45),
  [429] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 45), SHIFT(185),
  [432] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 3, .production_id = 26),
  [434] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 3, .production_id = 26), SHIFT(185),
  [437] = {.count = 1, .reusable = true}, SHIFT(90),
  [439] = {.count = 1, .reusable = true}, SHIFT(126),
  [441] = {.count = 1, .reusable = false}, REDUCE(sym_incomplete_amount, 2),
  [443] = {.count = 1, .reusable = true}, REDUCE(sym_incomplete_amount, 2),
  [445] = {.count = 1, .reusable = true}, SHIFT(220),
  [447] = {.count = 1, .reusable = true}, SHIFT(168),
  [449] = {.count = 1, .reusable = false}, REDUCE(aux_sym_tags_and_links_repeat1, 2),
  [451] = {.count = 2, .reusable = true}, REDUCE(aux_sym_tags_and_links_repeat1, 2), SHIFT_REPEAT(184),
  [454] = {.count = 2, .reusable = true}, REDUCE(aux_sym_tags_and_links_repeat1, 2), SHIFT_REPEAT(118),
  [457] = {.count = 1, .reusable = false}, SHIFT(25),
  [459] = {.count = 1, .reusable = true}, SHIFT(145),
  [461] = {.count = 1, .reusable = false}, REDUCE(sym_currency_list, 1),
  [463] = {.count = 1, .reusable = true}, REDUCE(sym_currency_list, 1),
  [465] = {.count = 1, .reusable = true}, SHIFT(241),
  [467] = {.count = 1, .reusable = false}, REDUCE(aux_sym_currency_list_repeat1, 2),
  [469] = {.count = 1, .reusable = true}, REDUCE(aux_sym_currency_list_repeat1, 2),
  [471] = {.count = 2, .reusable = true}, REDUCE(aux_sym_currency_list_repeat1, 2), SHIFT_REPEAT(241),
  [474] = {.count = 1, .reusable = true}, SHIFT(165),
  [476] = {.count = 1, .reusable = true}, SHIFT(193),
  [478] = {.count = 1, .reusable = false}, REDUCE(sym_currency_list, 2),
  [480] = {.count = 1, .reusable = true}, REDUCE(sym_currency_list, 2),
  [482] = {.count = 1, .reusable = true}, SHIFT(22),
  [484] = {.count = 1, .reusable = false}, REDUCE(sym_tags_and_links, 1),
  [486] = {.count = 2, .reusable = true}, REDUCE(sym_tags_and_links, 1), SHIFT(184),
  [489] = {.count = 1, .reusable = true}, SHIFT(118),
  [491] = {.count = 1, .reusable = true}, SHIFT(78),
  [493] = {.count = 1, .reusable = true}, SHIFT(74),
  [495] = {.count = 1, .reusable = false}, SHIFT(27),
  [497] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 54),
  [499] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 54), SHIFT(185),
  [502] = {.count = 1, .reusable = false}, SHIFT(17),
  [504] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 51),
  [506] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 51), SHIFT(185),
  [509] = {.count = 1, .reusable = false}, REDUCE(sym_cost_comp_list, 1),
  [511] = {.count = 1, .reusable = true}, REDUCE(sym_cost_comp_list, 1),
  [513] = {.count = 1, .reusable = true}, SHIFT(13),
  [515] = {.count = 1, .reusable = false}, SHIFT(36),
  [517] = {.count = 1, .reusable = false}, REDUCE(sym_cost_spec, 2),
  [519] = {.count = 1, .reusable = true}, REDUCE(sym_cost_spec, 2),
  [521] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 47),
  [523] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 47), SHIFT(185),
  [526] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 62),
  [528] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 62), SHIFT(185),
  [531] = {.count = 1, .reusable = true}, REDUCE(sym_txn_strings, 1),
  [533] = {.count = 1, .reusable = true}, SHIFT(175),
  [535] = {.count = 1, .reusable = false}, REDUCE(aux_sym_postings_repeat1, 2),
  [537] = {.count = 2, .reusable = true}, REDUCE(aux_sym_postings_repeat1, 2), SHIFT_REPEAT(166),
  [540] = {.count = 1, .reusable = true}, SHIFT(166),
  [542] = {.count = 1, .reusable = false}, REDUCE(aux_sym_cost_comp_list_repeat1, 2),
  [544] = {.count = 1, .reusable = true}, REDUCE(aux_sym_cost_comp_list_repeat1, 2),
  [546] = {.count = 2, .reusable = true}, REDUCE(aux_sym_cost_comp_list_repeat1, 2), SHIFT_REPEAT(13),
  [549] = {.count = 1, .reusable = false}, SHIFT(66),
  [551] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 65),
  [553] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 65), SHIFT(185),
  [556] = {.count = 1, .reusable = false}, SHIFT(16),
  [558] = {.count = 1, .reusable = false}, REDUCE(sym_postings, 1),
  [560] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 76),
  [562] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 76), SHIFT(185),
  [565] = {.count = 1, .reusable = false}, SHIFT(44),
  [567] = {.count = 1, .reusable = false}, REDUCE(sym_cost_spec, 3),
  [569] = {.count = 1, .reusable = true}, REDUCE(sym_cost_spec, 3),
  [571] = {.count = 1, .reusable = false}, REDUCE(sym_cost_comp_list, 2),
  [573] = {.count = 1, .reusable = true}, REDUCE(sym_cost_comp_list, 2),
  [575] = {.count = 1, .reusable = false}, SHIFT(15),
  [577] = {.count = 1, .reusable = false}, SHIFT(19),
  [579] = {.count = 1, .reusable = false}, SHIFT(23),
  [581] = {.count = 1, .reusable = true}, REDUCE(aux_sym_tags_and_links_repeat1, 2),
  [583] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 3, .production_id = 28),
  [585] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 3, .production_id = 28), SHIFT(185),
  [588] = {.count = 1, .reusable = false}, SHIFT(31),
  [590] = {.count = 1, .reusable = false}, SHIFT(28),
  [592] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 71),
  [594] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 71), SHIFT(185),
  [597] = {.count = 1, .reusable = false}, REDUCE(sym_compound_amount, 3, .production_id = 78),
  [599] = {.count = 1, .reusable = true}, REDUCE(sym_compound_amount, 3, .production_id = 78),
  [601] = {.count = 1, .reusable = false}, REDUCE(sym_metadata, 1),
  [603] = {.count = 1, .reusable = false}, REDUCE(sym_compound_amount, 4, .production_id = 82),
  [605] = {.count = 1, .reusable = true}, REDUCE(sym_compound_amount, 4, .production_id = 82),
  [607] = {.count = 1, .reusable = false}, REDUCE(sym_compound_amount, 1, .production_id = 48),
  [609] = {.count = 1, .reusable = true}, REDUCE(sym_compound_amount, 1, .production_id = 48),
  [611] = {.count = 1, .reusable = false}, REDUCE(sym_cost_comp, 1),
  [613] = {.count = 1, .reusable = true}, REDUCE(sym_cost_comp, 1),
  [615] = {.count = 1, .reusable = false}, REDUCE(sym_compound_amount, 3, .production_id = 79),
  [617] = {.count = 1, .reusable = true}, REDUCE(sym_compound_amount, 3, .production_id = 79),
  [619] = {.count = 1, .reusable = false}, REDUCE(aux_sym_metadata_repeat1, 2),
  [621] = {.count = 2, .reusable = true}, REDUCE(aux_sym_metadata_repeat1, 2), SHIFT_REPEAT(185),
  [624] = {.count = 1, .reusable = false}, REDUCE(sym_compound_amount, 2, .production_id = 68),
  [626] = {.count = 1, .reusable = true}, REDUCE(sym_compound_amount, 2, .production_id = 68),
  [628] = {.count = 1, .reusable = true}, REDUCE(sym_txn_strings, 2),
  [630] = {.count = 1, .reusable = false}, REDUCE(sym_compound_amount, 2, .production_id = 67),
  [632] = {.count = 1, .reusable = true}, REDUCE(sym_compound_amount, 2, .production_id = 67),
  [634] = {.count = 2, .reusable = true}, REDUCE(sym_metadata, 1), SHIFT(185),
  [637] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 63),
  [639] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 63),
  [641] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 7, .production_id = 81),
  [643] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 7, .production_id = 81),
  [645] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 66),
  [647] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 66),
  [649] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 75),
  [651] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 75),
  [653] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 77),
  [655] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 77),
  [657] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 70),
  [659] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 70),
  [661] = {.count = 1, .reusable = true}, REDUCE(aux_sym_metadata_repeat1, 2),
  [663] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 44),
  [665] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 44),
  [667] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 72),
  [669] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 72),
  [671] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 61),
  [673] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 61),
  [675] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 80),
  [677] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 80),
  [679] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 74),
  [681] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 74),
  [683] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 3, .production_id = 25),
  [685] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 3, .production_id = 25),
  [687] = {.count = 1, .reusable = false}, REDUCE(sym_amount_with_tolerance, 4),
  [689] = {.count = 1, .reusable = true}, REDUCE(sym_amount_with_tolerance, 4),
  [691] = {.count = 1, .reusable = true}, REDUCE(aux_sym_postings_repeat1, 2),
  [693] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 69),
  [695] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 69),
  [697] = {.count = 1, .reusable = false}, REDUCE(sym_key_value, 2),
  [699] = {.count = 1, .reusable = true}, REDUCE(sym_key_value, 2),
  [701] = {.count = 1, .reusable = false}, REDUCE(sym_price_annotation, 2),
  [703] = {.count = 1, .reusable = true}, REDUCE(sym_price_annotation, 2),
  [705] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 50),
  [707] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 50),
  [709] = {.count = 1, .reusable = true}, SHIFT(11),
  [711] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 52),
  [713] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 52),
  [715] = {.count = 1, .reusable = true}, SHIFT(40),
  [717] = {.count = 1, .reusable = true}, SHIFT(210),
  [719] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 55),
  [721] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 55),
  [723] = {.count = 1, .reusable = true}, SHIFT(46),
  [725] = {.count = 1, .reusable = true}, SHIFT(156),
  [727] = {.count = 1, .reusable = true}, SHIFT(154),
  [729] = {.count = 1, .reusable = true}, SHIFT(97),
  [731] = {.count = 1, .reusable = true}, SHIFT(38),
  [733] = {.count = 1, .reusable = true}, SHIFT(29),
  [735] = {.count = 1, .reusable = true}, SHIFT(68),
  [737] = {.count = 1, .reusable = true}, SHIFT(67),
  [739] = {.count = 1, .reusable = true}, SHIFT(216),
  [741] = {.count = 1, .reusable = true}, SHIFT(157),
  [743] = {.count = 1, .reusable = true}, SHIFT(132),
  [745] = {.count = 1, .reusable = true}, SHIFT(162),
  [747] = {.count = 1, .reusable = true}, SHIFT(87),
  [749] = {.count = 1, .reusable = true}, SHIFT(30),
  [751] = {.count = 1, .reusable = true}, SHIFT(33),
  [753] = {.count = 1, .reusable = true}, SHIFT(215),
  [755] = {.count = 1, .reusable = true}, SHIFT(47),
  [757] = {.count = 1, .reusable = true}, SHIFT(104),
  [759] = {.count = 1, .reusable = true}, SHIFT(34),
  [761] = {.count = 1, .reusable = true}, SHIFT(214),
  [763] = {.count = 1, .reusable = true}, SHIFT(53),
  [765] = {.count = 1, .reusable = true}, SHIFT(58),
  [767] = {.count = 1, .reusable = true}, SHIFT(39),
  [769] = {.count = 1, .reusable = true}, SHIFT(24),
  [771] = {.count = 1, .reusable = true}, SHIFT(41),
  [773] = {.count = 1, .reusable = true}, SHIFT(204),
  [775] = {.count = 1, .reusable = true}, SHIFT(5),
  [777] = {.count = 1, .reusable = true}, SHIFT(52),
  [779] = {.count = 1, .reusable = true}, SHIFT(60),
  [781] = {.count = 1, .reusable = true}, SHIFT(62),
  [783] = {.count = 1, .reusable = true}, SHIFT(54),
  [785] = {.count = 1, .reusable = true}, SHIFT(63),
  [787] = {.count = 1, .reusable = true}, SHIFT(64),
  [789] = {.count = 1, .reusable = true}, SHIFT(55),
  [791] = {.count = 1, .reusable = true}, SHIFT(206),
  [793] = {.count = 1, .reusable = true}, SHIFT(152),
  [795] = {.count = 1, .reusable = true}, SHIFT(50),
  [797] = {.count = 1, .reusable = true}, SHIFT(257),
  [799] = {.count = 1, .reusable = true}, SHIFT(7),
  [801] = {.count = 1, .reusable = true}, SHIFT(45),
  [803] = {.count = 1, .reusable = true}, SHIFT(148),
  [805] = {.count = 1, .reusable = true}, SHIFT(57),
  [807] = {.count = 1, .reusable = true}, SHIFT(137),
  [809] = {.count = 1, .reusable = true}, SHIFT(82),
  [811] = {.count = 1, .reusable = true}, SHIFT(49),
  [813] = {.count = 1, .reusable = true}, SHIFT(48),
  [815] = {.count = 1, .reusable = true}, SHIFT(43),
  [817] = {.count = 1, .reusable = true}, SHIFT(42),
  [819] = {.count = 1, .reusable = true}, SHIFT(35),
  [821] = {.count = 1, .reusable = true}, SHIFT(212),
  [823] = {.count = 1, .reusable = true}, SHIFT(14),
  [825] = {.count = 1, .reusable = true}, SHIFT(37),
  [827] = {.count = 1, .reusable = true},  ACCEPT_INPUT(),
  [829] = {.count = 1, .reusable = true}, SHIFT(250),
  [831] = {.count = 1, .reusable = true}, SHIFT(61),
  [833] = {.count = 1, .reusable = true}, SHIFT(252),
  [835] = {.count = 1, .reusable = true}, SHIFT(253),
  [837] = {.count = 1, .reusable = true}, SHIFT(201),
  [839] = {.count = 1, .reusable = true}, SHIFT(255),
  [841] = {.count = 1, .reusable = true}, SHIFT(256),
  [843] = {.count = 1, .reusable = true}, SHIFT(18),
};

#ifdef _WIN32
#define extern __declspec(dllexport)
#endif

extern const TSLanguage *tree_sitter_beancount(void) {
  static TSLanguage language = {
    .version = LANGUAGE_VERSION,
    .symbol_count = SYMBOL_COUNT,
    .alias_count = ALIAS_COUNT,
    .token_count = TOKEN_COUNT,
    .large_state_count = LARGE_STATE_COUNT,
    .symbol_metadata = ts_symbol_metadata,
    .parse_table = (const unsigned short *)ts_parse_table,
    .small_parse_table = (const uint16_t *)ts_small_parse_table,
    .small_parse_table_map = (const uint32_t *)ts_small_parse_table_map,
    .parse_actions = ts_parse_actions,
    .lex_modes = ts_lex_modes,
    .symbol_names = ts_symbol_names,
    .public_symbol_map = ts_symbol_map,
    .alias_sequences = (const TSSymbol *)ts_alias_sequences,
    .field_count = FIELD_COUNT,
    .field_names = ts_field_names,
    .field_map_slices = (const TSFieldMapSlice *)ts_field_map_slices,
    .field_map_entries = (const TSFieldMapEntry *)ts_field_map_entries,
    .max_alias_sequence_length = MAX_ALIAS_SEQUENCE_LENGTH,
    .lex_fn = ts_lex,
    .external_token_count = EXTERNAL_TOKEN_COUNT,
  };
  return &language;
}
