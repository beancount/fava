#include <tree_sitter/parser.h>

#if defined(__GNUC__) || defined(__clang__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#endif

#define LANGUAGE_VERSION 11
#define STATE_COUNT 300
#define LARGE_STATE_COUNT 2
#define SYMBOL_COUNT 100
#define ALIAS_COUNT 0
#define TOKEN_COUNT 49
#define EXTERNAL_TOKEN_COUNT 0
#define FIELD_COUNT 28
#define MAX_ALIAS_SEQUENCE_LENGTH 8

enum {
  aux_sym__skipped_lines_token1 = 1,
  aux_sym__skipped_lines_token2 = 2,
  aux_sym__skipped_lines_token3 = 3,
  anon_sym_COLON = 4,
  aux_sym__skipped_lines_token4 = 5,
  aux_sym_metadata_token1 = 6,
  anon_sym_include = 7,
  anon_sym_option = 8,
  anon_sym_plugin = 9,
  anon_sym_pushtag = 10,
  anon_sym_poptag = 11,
  anon_sym_pushmeta = 12,
  anon_sym_popmeta = 13,
  anon_sym_LBRACE = 14,
  anon_sym_RBRACE = 15,
  anon_sym_LBRACE_LBRACE = 16,
  anon_sym_RBRACE_RBRACE = 17,
  anon_sym_COMMA = 18,
  anon_sym_STAR = 19,
  anon_sym_POUND = 20,
  anon_sym_AT_AT = 21,
  anon_sym_AT = 22,
  anon_sym_balance = 23,
  anon_sym_close = 24,
  anon_sym_commodity = 25,
  anon_sym_custom = 26,
  anon_sym_document = 27,
  anon_sym_event = 28,
  anon_sym_note = 29,
  anon_sym_open = 30,
  anon_sym_pad = 31,
  anon_sym_price = 32,
  anon_sym_query = 33,
  anon_sym_TILDE = 34,
  anon_sym_LPAREN = 35,
  anon_sym_RPAREN = 36,
  anon_sym_DASH = 37,
  anon_sym_PLUS = 38,
  anon_sym_SLASH = 39,
  sym_bool = 40,
  sym_date = 41,
  sym_key = 42,
  sym_tag = 43,
  sym_link = 44,
  sym_string = 45,
  sym_currency = 46,
  sym_number = 47,
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
  sym_flag = 92,
  aux_sym_beancount_file_repeat1 = 93,
  aux_sym_metadata_repeat1 = 94,
  aux_sym_cost_comp_list_repeat1 = 95,
  aux_sym_postings_repeat1 = 96,
  aux_sym_tags_and_links_repeat1 = 97,
  aux_sym_custom_repeat1 = 98,
  aux_sym_currency_list_repeat1 = 99,
};

static const char *ts_symbol_names[] = {
  [ts_builtin_sym_end] = "end",
  [aux_sym__skipped_lines_token1] = "_skipped_lines_token1",
  [aux_sym__skipped_lines_token2] = "_skipped_lines_token2",
  [aux_sym__skipped_lines_token3] = "_skipped_lines_token3",
  [anon_sym_COLON] = ":",
  [aux_sym__skipped_lines_token4] = "_skipped_lines_token4",
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
  [sym_flag] = "flag",
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
  [aux_sym__skipped_lines_token3] = aux_sym__skipped_lines_token3,
  [anon_sym_COLON] = anon_sym_COLON,
  [aux_sym__skipped_lines_token4] = aux_sym__skipped_lines_token4,
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
  [sym_flag] = sym_flag,
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
  [aux_sym__skipped_lines_token3] = {
    .visible = false,
    .named = false,
  },
  [anon_sym_COLON] = {
    .visible = true,
    .named = false,
  },
  [aux_sym__skipped_lines_token4] = {
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
  [sym_flag] = {
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
  field_cost_comp_list = 5,
  field_cost_spec = 6,
  field_currencies = 7,
  field_currency = 8,
  field_date = 9,
  field_description = 10,
  field_filename = 11,
  field_flag = 12,
  field_from_account = 13,
  field_key = 14,
  field_key_value = 15,
  field_metadata = 16,
  field_name = 17,
  field_note = 18,
  field_number_per = 19,
  field_number_total = 20,
  field_postings = 21,
  field_price_annotation = 22,
  field_query = 23,
  field_tag = 24,
  field_tags_and_links = 25,
  field_txn_strings = 26,
  field_type = 27,
  field_value = 28,
};

static const char *ts_field_names[] = {
  [0] = NULL,
  [field_account] = "account",
  [field_amount] = "amount",
  [field_booking] = "booking",
  [field_config] = "config",
  [field_cost_comp_list] = "cost_comp_list",
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

static const TSFieldMapSlice ts_field_map_slices[100] = {
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
  [44] = {.index = 123, .length = 2},
  [45] = {.index = 125, .length = 1},
  [46] = {.index = 126, .length = 1},
  [47] = {.index = 127, .length = 3},
  [48] = {.index = 130, .length = 3},
  [49] = {.index = 133, .length = 3},
  [50] = {.index = 136, .length = 3},
  [51] = {.index = 139, .length = 3},
  [52] = {.index = 142, .length = 3},
  [53] = {.index = 145, .length = 3},
  [54] = {.index = 148, .length = 3},
  [55] = {.index = 151, .length = 3},
  [56] = {.index = 154, .length = 3},
  [57] = {.index = 157, .length = 5},
  [58] = {.index = 162, .length = 5},
  [59] = {.index = 167, .length = 5},
  [60] = {.index = 172, .length = 5},
  [61] = {.index = 177, .length = 5},
  [62] = {.index = 182, .length = 1},
  [63] = {.index = 183, .length = 1},
  [64] = {.index = 184, .length = 2},
  [65] = {.index = 186, .length = 3},
  [66] = {.index = 189, .length = 4},
  [67] = {.index = 193, .length = 3},
  [68] = {.index = 196, .length = 4},
  [69] = {.index = 200, .length = 4},
  [70] = {.index = 204, .length = 4},
  [71] = {.index = 208, .length = 3},
  [72] = {.index = 211, .length = 3},
  [73] = {.index = 214, .length = 4},
  [74] = {.index = 218, .length = 4},
  [75] = {.index = 222, .length = 4},
  [76] = {.index = 226, .length = 4},
  [77] = {.index = 230, .length = 4},
  [78] = {.index = 234, .length = 4},
  [79] = {.index = 238, .length = 6},
  [80] = {.index = 244, .length = 2},
  [81] = {.index = 246, .length = 2},
  [82] = {.index = 248, .length = 4},
  [83] = {.index = 252, .length = 4},
  [84] = {.index = 256, .length = 5},
  [85] = {.index = 261, .length = 4},
  [86] = {.index = 265, .length = 4},
  [87] = {.index = 269, .length = 5},
  [88] = {.index = 274, .length = 4},
  [89] = {.index = 278, .length = 5},
  [90] = {.index = 283, .length = 5},
  [91] = {.index = 288, .length = 5},
  [92] = {.index = 293, .length = 4},
  [93] = {.index = 297, .length = 3},
  [94] = {.index = 300, .length = 5},
  [95] = {.index = 305, .length = 5},
  [96] = {.index = 310, .length = 5},
  [97] = {.index = 315, .length = 6},
  [98] = {.index = 321, .length = 5},
  [99] = {.index = 326, .length = 6},
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
    {field_account, 1},
    {field_metadata, 2},
  [56] =
    {field_account, 1},
    {field_cost_spec, 2},
  [58] =
    {field_account, 1},
    {field_amount, 2},
  [60] =
    {field_account, 1},
    {field_price_annotation, 2},
  [62] =
    {field_account, 2},
    {field_flag, 1},
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
    {field_account, 1},
    {field_metadata, 3},
  [125] =
    {field_currency, 0},
  [126] =
    {field_number_per, 0},
  [127] =
    {field_account, 1},
    {field_cost_spec, 2},
    {field_metadata, 3},
  [130] =
    {field_account, 1},
    {field_cost_spec, 2},
    {field_price_annotation, 3},
  [133] =
    {field_account, 1},
    {field_amount, 2},
    {field_metadata, 3},
  [136] =
    {field_account, 1},
    {field_amount, 2},
    {field_cost_spec, 3},
  [139] =
    {field_account, 1},
    {field_amount, 2},
    {field_price_annotation, 3},
  [142] =
    {field_account, 1},
    {field_metadata, 3},
    {field_price_annotation, 2},
  [145] =
    {field_account, 2},
    {field_flag, 1},
    {field_metadata, 3},
  [148] =
    {field_account, 2},
    {field_cost_spec, 3},
    {field_flag, 1},
  [151] =
    {field_account, 2},
    {field_amount, 3},
    {field_flag, 1},
  [154] =
    {field_account, 2},
    {field_flag, 1},
    {field_price_annotation, 3},
  [157] =
    {field_date, 0},
    {field_flag, 1},
    {field_metadata, 3},
    {field_postings, 4},
    {field_tags_and_links, 2},
  [162] =
    {field_date, 0},
    {field_flag, 1},
    {field_metadata, 3},
    {field_postings, 4},
    {field_txn_strings, 2},
  [167] =
    {field_date, 0},
    {field_flag, 1},
    {field_postings, 4},
    {field_tags_and_links, 3},
    {field_txn_strings, 2},
  [172] =
    {field_account, 2},
    {field_date, 0},
    {field_filename, 3},
    {field_metadata, 5},
    {field_tags_and_links, 4},
  [177] =
    {field_account, 2},
    {field_booking, 4},
    {field_currencies, 3},
    {field_date, 0},
    {field_metadata, 5},
  [182] =
    {field_currency, 1},
  [183] =
    {field_cost_comp_list, 1},
  [184] =
    {field_currency, 1},
    {field_number_per, 0},
  [186] =
    {field_account, 1},
    {field_cost_spec, 2},
    {field_metadata, 4},
  [189] =
    {field_account, 1},
    {field_cost_spec, 2},
    {field_metadata, 4},
    {field_price_annotation, 3},
  [193] =
    {field_account, 1},
    {field_amount, 2},
    {field_metadata, 4},
  [196] =
    {field_account, 1},
    {field_amount, 2},
    {field_cost_spec, 3},
    {field_metadata, 4},
  [200] =
    {field_account, 1},
    {field_amount, 2},
    {field_cost_spec, 3},
    {field_price_annotation, 4},
  [204] =
    {field_account, 1},
    {field_amount, 2},
    {field_metadata, 4},
    {field_price_annotation, 3},
  [208] =
    {field_account, 1},
    {field_metadata, 4},
    {field_price_annotation, 2},
  [211] =
    {field_account, 2},
    {field_flag, 1},
    {field_metadata, 4},
  [214] =
    {field_account, 2},
    {field_cost_spec, 3},
    {field_flag, 1},
    {field_metadata, 4},
  [218] =
    {field_account, 2},
    {field_cost_spec, 3},
    {field_flag, 1},
    {field_price_annotation, 4},
  [222] =
    {field_account, 2},
    {field_amount, 3},
    {field_flag, 1},
    {field_metadata, 4},
  [226] =
    {field_account, 2},
    {field_amount, 3},
    {field_cost_spec, 4},
    {field_flag, 1},
  [230] =
    {field_account, 2},
    {field_amount, 3},
    {field_flag, 1},
    {field_price_annotation, 4},
  [234] =
    {field_account, 2},
    {field_flag, 1},
    {field_metadata, 4},
    {field_price_annotation, 3},
  [238] =
    {field_date, 0},
    {field_flag, 1},
    {field_metadata, 4},
    {field_postings, 5},
    {field_tags_and_links, 3},
    {field_txn_strings, 2},
  [244] =
    {field_currency, 2},
    {field_number_total, 1},
  [246] =
    {field_currency, 2},
    {field_number_per, 0},
  [248] =
    {field_account, 1},
    {field_cost_spec, 2},
    {field_metadata, 5},
    {field_price_annotation, 3},
  [252] =
    {field_account, 1},
    {field_amount, 2},
    {field_cost_spec, 3},
    {field_metadata, 5},
  [256] =
    {field_account, 1},
    {field_amount, 2},
    {field_cost_spec, 3},
    {field_metadata, 5},
    {field_price_annotation, 4},
  [261] =
    {field_account, 1},
    {field_amount, 2},
    {field_metadata, 5},
    {field_price_annotation, 3},
  [265] =
    {field_account, 2},
    {field_cost_spec, 3},
    {field_flag, 1},
    {field_metadata, 5},
  [269] =
    {field_account, 2},
    {field_cost_spec, 3},
    {field_flag, 1},
    {field_metadata, 5},
    {field_price_annotation, 4},
  [274] =
    {field_account, 2},
    {field_amount, 3},
    {field_flag, 1},
    {field_metadata, 5},
  [278] =
    {field_account, 2},
    {field_amount, 3},
    {field_cost_spec, 4},
    {field_flag, 1},
    {field_metadata, 5},
  [283] =
    {field_account, 2},
    {field_amount, 3},
    {field_cost_spec, 4},
    {field_flag, 1},
    {field_price_annotation, 5},
  [288] =
    {field_account, 2},
    {field_amount, 3},
    {field_flag, 1},
    {field_metadata, 5},
    {field_price_annotation, 4},
  [293] =
    {field_account, 2},
    {field_flag, 1},
    {field_metadata, 5},
    {field_price_annotation, 3},
  [297] =
    {field_currency, 3},
    {field_number_per, 0},
    {field_number_total, 2},
  [300] =
    {field_account, 1},
    {field_amount, 2},
    {field_cost_spec, 3},
    {field_metadata, 6},
    {field_price_annotation, 4},
  [305] =
    {field_account, 2},
    {field_cost_spec, 3},
    {field_flag, 1},
    {field_metadata, 6},
    {field_price_annotation, 4},
  [310] =
    {field_account, 2},
    {field_amount, 3},
    {field_cost_spec, 4},
    {field_flag, 1},
    {field_metadata, 6},
  [315] =
    {field_account, 2},
    {field_amount, 3},
    {field_cost_spec, 4},
    {field_flag, 1},
    {field_metadata, 6},
    {field_price_annotation, 5},
  [321] =
    {field_account, 2},
    {field_amount, 3},
    {field_flag, 1},
    {field_metadata, 6},
    {field_price_annotation, 4},
  [326] =
    {field_account, 2},
    {field_amount, 3},
    {field_cost_spec, 4},
    {field_flag, 1},
    {field_metadata, 7},
    {field_price_annotation, 5},
};

static TSSymbol ts_alias_sequences[100][MAX_ALIAS_SEQUENCE_LENGTH] = {
  [0] = {0},
};

static bool ts_lex(TSLexer *lexer, TSStateId state) {
  START_LEXER();
  eof = lexer->eof(lexer);
  switch (state) {
    case 0:
      if (eof) ADVANCE(156);
      if (lookahead == '\n') ADVANCE(163);
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == '#') ADVANCE(181);
      if (lookahead == '(') ADVANCE(196);
      if (lookahead == ')') ADVANCE(197);
      if (lookahead == '*') ADVANCE(180);
      if (lookahead == '+') ADVANCE(199);
      if (lookahead == ',') ADVANCE(179);
      if (lookahead == '-') ADVANCE(198);
      if (lookahead == '/') ADVANCE(200);
      if (lookahead == ':') ADVANCE(164);
      if (lookahead == ';') ADVANCE(165);
      if (lookahead == '@') ADVANCE(183);
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
      if (lookahead == '{') ADVANCE(174);
      if (lookahead == '}') ADVANCE(176);
      if (lookahead == '~') ADVANCE(195);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(0)
      if (lookahead == '!' ||
          lookahead == '%' ||
          lookahead == '&' ||
          lookahead == '?') ADVANCE(157);
      if (lookahead == 'C' ||
          lookahead == 'M' ||
          lookahead == 'P' ||
          ('R' <= lookahead && lookahead <= 'U')) ADVANCE(158);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(263);
      if (lookahead != 0 &&
          (lookahead < 0 || '>' < lookahead) &&
          (lookahead < '[' || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 1:
      if (lookahead == '\n') ADVANCE(163);
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == '#') ADVANCE(153);
      if (lookahead == '(') ADVANCE(196);
      if (lookahead == ')') ADVANCE(197);
      if (lookahead == '*') ADVANCE(180);
      if (lookahead == '+') ADVANCE(199);
      if (lookahead == '-') ADVANCE(198);
      if (lookahead == '/') ADVANCE(200);
      if (lookahead == ';') ADVANCE(165);
      if (lookahead == '@') ADVANCE(183);
      if (lookahead == '^') ADVANCE(152);
      if (lookahead == '{') ADVANCE(174);
      if (lookahead == '}') ADVANCE(175);
      if (lookahead == '~') ADVANCE(195);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(1)
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(264);
      if (('A' <= lookahead && lookahead <= 'Z')) ADVANCE(143);
      if (('a' <= lookahead && lookahead <= 'z')) ADVANCE(151);
      END_STATE();
    case 2:
      if (lookahead == '\n') ADVANCE(163);
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == '#') ADVANCE(153);
      if (lookahead == '(') ADVANCE(196);
      if (lookahead == '*') ADVANCE(180);
      if (lookahead == '+') ADVANCE(199);
      if (lookahead == '-') ADVANCE(198);
      if (lookahead == '/') ADVANCE(200);
      if (lookahead == 'F') ADVANCE(32);
      if (lookahead == 'T') ADVANCE(33);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(2)
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(263);
      if (('A' <= lookahead && lookahead <= 'Z')) ADVANCE(34);
      if (lookahead != 0 &&
          (lookahead < 0 || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 3:
      if (lookahead == '\n') ADVANCE(163);
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == '#') ADVANCE(153);
      if (lookahead == '(') ADVANCE(196);
      if (lookahead == '+') ADVANCE(199);
      if (lookahead == '-') ADVANCE(198);
      if (lookahead == 'F') ADVANCE(35);
      if (lookahead == 'T') ADVANCE(38);
      if (lookahead == '^') ADVANCE(152);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(3)
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(263);
      if (lookahead != 0 &&
          (lookahead < 0 || '@' < lookahead) &&
          (lookahead < '[' || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 4:
      if (lookahead == '\n') ADVANCE(162);
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == '#') ADVANCE(181);
      if (lookahead == '(') ADVANCE(196);
      if (lookahead == '*') ADVANCE(180);
      if (lookahead == '+') ADVANCE(199);
      if (lookahead == '-') ADVANCE(198);
      if (lookahead == '/') ADVANCE(200);
      if (lookahead == '}') ADVANCE(175);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(4)
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(263);
      if (('A' <= lookahead && lookahead <= 'Z')) ADVANCE(143);
      END_STATE();
    case 5:
      if (lookahead == '\n') ADVANCE(162);
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == '#') ADVANCE(153);
      if (lookahead == '(') ADVANCE(196);
      if (lookahead == '+') ADVANCE(199);
      if (lookahead == '-') ADVANCE(198);
      if (lookahead == 'F') ADVANCE(32);
      if (lookahead == 'T') ADVANCE(33);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(5)
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(263);
      if (('A' <= lookahead && lookahead <= 'Z')) ADVANCE(34);
      if (lookahead != 0 &&
          (lookahead < 0 || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 6:
      if (lookahead == '\n') ADVANCE(162);
      if (lookahead == '#') ADVANCE(181);
      if (lookahead == ')') ADVANCE(197);
      if (lookahead == '*') ADVANCE(180);
      if (lookahead == '+') ADVANCE(199);
      if (lookahead == ',') ADVANCE(179);
      if (lookahead == '-') ADVANCE(198);
      if (lookahead == '/') ADVANCE(200);
      if (lookahead == '}') ADVANCE(176);
      if (lookahead == '~') ADVANCE(195);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(6)
      if (('A' <= lookahead && lookahead <= 'Z')) ADVANCE(143);
      END_STATE();
    case 7:
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == '#') ADVANCE(181);
      if (lookahead == '(') ADVANCE(196);
      if (lookahead == '*') ADVANCE(180);
      if (lookahead == '+') ADVANCE(199);
      if (lookahead == '-') ADVANCE(198);
      if (lookahead == '}') ADVANCE(120);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(7)
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(263);
      if (('A' <= lookahead && lookahead <= 'Z')) ADVANCE(143);
      END_STATE();
    case 8:
      if (lookahead == '"') ADVANCE(208);
      if (lookahead != 0) ADVANCE(8);
      END_STATE();
    case 9:
      if (lookahead == '#') ADVANCE(159);
      if (lookahead == ';') ADVANCE(165);
      if (lookahead == '^') ADVANCE(152);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(9)
      if (lookahead == '!' ||
          lookahead == '%' ||
          lookahead == '&' ||
          lookahead == '*' ||
          lookahead == '?') ADVANCE(157);
      if (lookahead == 'C' ||
          lookahead == 'M' ||
          lookahead == 'P' ||
          ('R' <= lookahead && lookahead <= 'U')) ADVANCE(158);
      if (lookahead != 0 &&
          (lookahead < 0 || '@' < lookahead) &&
          (lookahead < '[' || 127 < lookahead)) ADVANCE(41);
      if (('a' <= lookahead && lookahead <= 'z')) ADVANCE(151);
      END_STATE();
    case 10:
      if (lookahead == ',') ADVANCE(10);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(264);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(237);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(212);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(210);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(214);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(211);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(216);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(213);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(218);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(215);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(220);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(217);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(222);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(219);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(224);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(221);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(226);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(223);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(229);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(225);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(235);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(228);
      END_STATE();
    case 32:
      if (lookahead == '-') ADVANCE(30);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'A') ADVANCE(230);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(144);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('B' <= lookahead && lookahead <= 'Z')) ADVANCE(232);
      END_STATE();
    case 33:
      if (lookahead == '-') ADVANCE(30);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'R') ADVANCE(231);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(144);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(232);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(232);
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
      if (lookahead == 'E') ADVANCE(203);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(236);
      END_STATE();
    case 43:
      if (lookahead == ':') ADVANCE(205);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(43);
      END_STATE();
    case 44:
      if (lookahead == ';') ADVANCE(165);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(44)
      if (lookahead == '!' ||
          lookahead == '#' ||
          lookahead == '%' ||
          lookahead == '&' ||
          lookahead == '*' ||
          lookahead == '?') ADVANCE(157);
      if (lookahead == 'C' ||
          lookahead == 'M' ||
          lookahead == 'P' ||
          ('R' <= lookahead && lookahead <= 'U')) ADVANCE(158);
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
      if (lookahead == 'a') ADVANCE(173);
      END_STATE();
    case 48:
      if (lookahead == 'a') ADVANCE(172);
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
      if (lookahead == 'd') ADVANCE(192);
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
      if (lookahead == 'e') ADVANCE(190);
      END_STATE();
    case 61:
      if (lookahead == 'e') ADVANCE(185);
      END_STATE();
    case 62:
      if (lookahead == 'e') ADVANCE(193);
      END_STATE();
    case 63:
      if (lookahead == 'e') ADVANCE(184);
      END_STATE();
    case 64:
      if (lookahead == 'e') ADVANCE(167);
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
      if (lookahead == 'g') ADVANCE(171);
      END_STATE();
    case 71:
      if (lookahead == 'g') ADVANCE(170);
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
      if (lookahead == 'm') ADVANCE(187);
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
      if (lookahead == 'n') ADVANCE(191);
      END_STATE();
    case 88:
      if (lookahead == 'n') ADVANCE(168);
      END_STATE();
    case 89:
      if (lookahead == 'n') ADVANCE(169);
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
      if (lookahead == 't') ADVANCE(189);
      END_STATE();
    case 107:
      if (lookahead == 't') ADVANCE(188);
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
      if (lookahead == 'y') ADVANCE(194);
      END_STATE();
    case 119:
      if (lookahead == 'y') ADVANCE(186);
      END_STATE();
    case 120:
      if (lookahead == '}') ADVANCE(178);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(259);
      END_STATE();
    case 124:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(123);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(238);
      END_STATE();
    case 125:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(126);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(241);
      END_STATE();
    case 126:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(124);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(239);
      END_STATE();
    case 127:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(128);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(243);
      END_STATE();
    case 128:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(125);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(240);
      END_STATE();
    case 129:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(130);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(245);
      END_STATE();
    case 130:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(127);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(242);
      END_STATE();
    case 131:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(132);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(247);
      END_STATE();
    case 132:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(129);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(244);
      END_STATE();
    case 133:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(134);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(249);
      END_STATE();
    case 134:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(131);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(246);
      END_STATE();
    case 135:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(136);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(251);
      END_STATE();
    case 136:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(133);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(248);
      END_STATE();
    case 137:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(138);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(253);
      END_STATE();
    case 138:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(135);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(250);
      END_STATE();
    case 139:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(140);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(255);
      END_STATE();
    case 140:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(137);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(252);
      END_STATE();
    case 141:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(142);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(257);
      END_STATE();
    case 142:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(139);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(254);
      END_STATE();
    case 143:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(144);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(258);
      END_STATE();
    case 144:
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(141);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(256);
      END_STATE();
    case 145:
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(204);
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(209);
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
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(207);
      END_STATE();
    case 153:
      if (('-' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(206);
      END_STATE();
    case 154:
      if (lookahead != 0 &&
          (lookahead < 0 || '/' < lookahead) &&
          (lookahead < ':' || '@' < lookahead) &&
          (lookahead < '[' || 127 < lookahead)) ADVANCE(269);
      END_STATE();
    case 155:
      if (eof) ADVANCE(156);
      if (lookahead == '\n') ADVANCE(162);
      if (lookahead == '"') ADVANCE(8);
      if (lookahead == ':') ADVANCE(164);
      if (lookahead == ';') ADVANCE(165);
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
          ('R' <= lookahead && lookahead <= 'U')) ADVANCE(157);
      END_STATE();
    case 156:
      ACCEPT_TOKEN(ts_builtin_sym_end);
      END_STATE();
    case 157:
      ACCEPT_TOKEN(aux_sym__skipped_lines_token1);
      END_STATE();
    case 158:
      ACCEPT_TOKEN(aux_sym__skipped_lines_token1);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead != 0 &&
          (lookahead < 0 || ',' < lookahead) &&
          lookahead != '.' &&
          lookahead != '/' &&
          (lookahead < ';' || '@' < lookahead) &&
          (lookahead < '[' || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      END_STATE();
    case 159:
      ACCEPT_TOKEN(aux_sym__skipped_lines_token1);
      if (('-' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(206);
      END_STATE();
    case 160:
      ACCEPT_TOKEN(aux_sym__skipped_lines_token2);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') ADVANCE(160);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(161);
      END_STATE();
    case 161:
      ACCEPT_TOKEN(aux_sym__skipped_lines_token2);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(161);
      END_STATE();
    case 162:
      ACCEPT_TOKEN(aux_sym__skipped_lines_token3);
      END_STATE();
    case 163:
      ACCEPT_TOKEN(aux_sym__skipped_lines_token3);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') ADVANCE(166);
      END_STATE();
    case 164:
      ACCEPT_TOKEN(anon_sym_COLON);
      END_STATE();
    case 165:
      ACCEPT_TOKEN(aux_sym__skipped_lines_token4);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(165);
      END_STATE();
    case 166:
      ACCEPT_TOKEN(aux_sym_metadata_token1);
      if (lookahead == '\t' ||
          lookahead == '\r' ||
          lookahead == ' ') ADVANCE(166);
      END_STATE();
    case 167:
      ACCEPT_TOKEN(anon_sym_include);
      END_STATE();
    case 168:
      ACCEPT_TOKEN(anon_sym_option);
      END_STATE();
    case 169:
      ACCEPT_TOKEN(anon_sym_plugin);
      END_STATE();
    case 170:
      ACCEPT_TOKEN(anon_sym_pushtag);
      END_STATE();
    case 171:
      ACCEPT_TOKEN(anon_sym_poptag);
      END_STATE();
    case 172:
      ACCEPT_TOKEN(anon_sym_pushmeta);
      END_STATE();
    case 173:
      ACCEPT_TOKEN(anon_sym_popmeta);
      END_STATE();
    case 174:
      ACCEPT_TOKEN(anon_sym_LBRACE);
      if (lookahead == '{') ADVANCE(177);
      END_STATE();
    case 175:
      ACCEPT_TOKEN(anon_sym_RBRACE);
      END_STATE();
    case 176:
      ACCEPT_TOKEN(anon_sym_RBRACE);
      if (lookahead == '}') ADVANCE(178);
      END_STATE();
    case 177:
      ACCEPT_TOKEN(anon_sym_LBRACE_LBRACE);
      END_STATE();
    case 178:
      ACCEPT_TOKEN(anon_sym_RBRACE_RBRACE);
      END_STATE();
    case 179:
      ACCEPT_TOKEN(anon_sym_COMMA);
      END_STATE();
    case 180:
      ACCEPT_TOKEN(anon_sym_STAR);
      END_STATE();
    case 181:
      ACCEPT_TOKEN(anon_sym_POUND);
      END_STATE();
    case 182:
      ACCEPT_TOKEN(anon_sym_AT_AT);
      END_STATE();
    case 183:
      ACCEPT_TOKEN(anon_sym_AT);
      if (lookahead == '@') ADVANCE(182);
      END_STATE();
    case 184:
      ACCEPT_TOKEN(anon_sym_balance);
      END_STATE();
    case 185:
      ACCEPT_TOKEN(anon_sym_close);
      END_STATE();
    case 186:
      ACCEPT_TOKEN(anon_sym_commodity);
      END_STATE();
    case 187:
      ACCEPT_TOKEN(anon_sym_custom);
      END_STATE();
    case 188:
      ACCEPT_TOKEN(anon_sym_document);
      END_STATE();
    case 189:
      ACCEPT_TOKEN(anon_sym_event);
      END_STATE();
    case 190:
      ACCEPT_TOKEN(anon_sym_note);
      END_STATE();
    case 191:
      ACCEPT_TOKEN(anon_sym_open);
      END_STATE();
    case 192:
      ACCEPT_TOKEN(anon_sym_pad);
      END_STATE();
    case 193:
      ACCEPT_TOKEN(anon_sym_price);
      END_STATE();
    case 194:
      ACCEPT_TOKEN(anon_sym_query);
      END_STATE();
    case 195:
      ACCEPT_TOKEN(anon_sym_TILDE);
      END_STATE();
    case 196:
      ACCEPT_TOKEN(anon_sym_LPAREN);
      END_STATE();
    case 197:
      ACCEPT_TOKEN(anon_sym_RPAREN);
      END_STATE();
    case 198:
      ACCEPT_TOKEN(anon_sym_DASH);
      END_STATE();
    case 199:
      ACCEPT_TOKEN(anon_sym_PLUS);
      END_STATE();
    case 200:
      ACCEPT_TOKEN(anon_sym_SLASH);
      END_STATE();
    case 201:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(229);
      END_STATE();
    case 202:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(225);
      END_STATE();
    case 203:
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
    case 204:
      ACCEPT_TOKEN(sym_date);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(204);
      END_STATE();
    case 205:
      ACCEPT_TOKEN(sym_key);
      END_STATE();
    case 206:
      ACCEPT_TOKEN(sym_tag);
      if (('-' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(206);
      END_STATE();
    case 207:
      ACCEPT_TOKEN(sym_link);
      if (('-' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(207);
      END_STATE();
    case 208:
      ACCEPT_TOKEN(sym_string);
      END_STATE();
    case 209:
      ACCEPT_TOKEN(sym_currency);
      END_STATE();
    case 210:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(237);
      END_STATE();
    case 211:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(212);
      END_STATE();
    case 212:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(210);
      END_STATE();
    case 213:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(214);
      END_STATE();
    case 214:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(211);
      END_STATE();
    case 215:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(216);
      END_STATE();
    case 216:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(213);
      END_STATE();
    case 217:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(218);
      END_STATE();
    case 218:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(215);
      END_STATE();
    case 219:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(220);
      END_STATE();
    case 220:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(217);
      END_STATE();
    case 221:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(222);
      END_STATE();
    case 222:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(219);
      END_STATE();
    case 223:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(224);
      END_STATE();
    case 224:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(221);
      END_STATE();
    case 225:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(226);
      END_STATE();
    case 226:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(223);
      END_STATE();
    case 227:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(29);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'E') ADVANCE(202);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(139);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(229);
      END_STATE();
    case 228:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(229);
      END_STATE();
    case 229:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(225);
      END_STATE();
    case 230:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(31);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'L') ADVANCE(234);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(141);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(235);
      END_STATE();
    case 231:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(31);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'U') ADVANCE(233);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(141);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(235);
      END_STATE();
    case 232:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(235);
      END_STATE();
    case 233:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(28);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'E') ADVANCE(201);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(142);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(228);
      END_STATE();
    case 234:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '-') ADVANCE(28);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead == 'S') ADVANCE(227);
      if (lookahead == '\'' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(142);
      if (lookahead != 0 &&
          (lookahead < 0 || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(228);
      END_STATE();
    case 235:
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
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(228);
      END_STATE();
    case 236:
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
    case 237:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == ':') ADVANCE(154);
      if (lookahead != 0 &&
          (lookahead < 0 || ',' < lookahead) &&
          (lookahead < '.' || '`' < lookahead) &&
          (lookahead < '{' || 127 < lookahead)) ADVANCE(41);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(236);
      END_STATE();
    case 238:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(150);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(259);
      END_STATE();
    case 239:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(123);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(238);
      END_STATE();
    case 240:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(126);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(241);
      END_STATE();
    case 241:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(124);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(239);
      END_STATE();
    case 242:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(128);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(243);
      END_STATE();
    case 243:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(125);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(240);
      END_STATE();
    case 244:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(130);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(245);
      END_STATE();
    case 245:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(127);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(242);
      END_STATE();
    case 246:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(132);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(247);
      END_STATE();
    case 247:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(129);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(244);
      END_STATE();
    case 248:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(134);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(249);
      END_STATE();
    case 249:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(131);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(246);
      END_STATE();
    case 250:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(136);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(251);
      END_STATE();
    case 251:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(133);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(248);
      END_STATE();
    case 252:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(138);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(253);
      END_STATE();
    case 253:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(135);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(250);
      END_STATE();
    case 254:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(140);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(255);
      END_STATE();
    case 255:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(137);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(252);
      END_STATE();
    case 256:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(142);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(257);
      END_STATE();
    case 257:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(139);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(254);
      END_STATE();
    case 258:
      ACCEPT_TOKEN(sym_currency);
      if (lookahead == '\'' ||
          lookahead == '-' ||
          lookahead == '.' ||
          lookahead == '_') ADVANCE(141);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(256);
      END_STATE();
    case 259:
      ACCEPT_TOKEN(sym_currency);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z')) ADVANCE(209);
      END_STATE();
    case 260:
      ACCEPT_TOKEN(sym_number);
      if (lookahead == ',') ADVANCE(265);
      if (lookahead == '-' ||
          lookahead == '/') ADVANCE(268);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(264);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(267);
      END_STATE();
    case 261:
      ACCEPT_TOKEN(sym_number);
      if (lookahead == ',') ADVANCE(265);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(260);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(267);
      END_STATE();
    case 262:
      ACCEPT_TOKEN(sym_number);
      if (lookahead == ',') ADVANCE(265);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(261);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(267);
      END_STATE();
    case 263:
      ACCEPT_TOKEN(sym_number);
      if (lookahead == ',') ADVANCE(265);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(262);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(267);
      END_STATE();
    case 264:
      ACCEPT_TOKEN(sym_number);
      if (lookahead == ',') ADVANCE(265);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(264);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(267);
      END_STATE();
    case 265:
      ACCEPT_TOKEN(sym_number);
      if (lookahead == ',') ADVANCE(10);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(264);
      END_STATE();
    case 266:
      ACCEPT_TOKEN(sym_number);
      if (lookahead == '-' ||
          lookahead == '/') ADVANCE(145);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(266);
      END_STATE();
    case 267:
      ACCEPT_TOKEN(sym_number);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(267);
      END_STATE();
    case 268:
      ACCEPT_TOKEN(sym_number);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(266);
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
  [9] = {.lex_state = 5},
  [10] = {.lex_state = 4},
  [11] = {.lex_state = 7},
  [12] = {.lex_state = 3},
  [13] = {.lex_state = 4},
  [14] = {.lex_state = 155},
  [15] = {.lex_state = 155},
  [16] = {.lex_state = 155},
  [17] = {.lex_state = 155},
  [18] = {.lex_state = 155},
  [19] = {.lex_state = 155},
  [20] = {.lex_state = 2},
  [21] = {.lex_state = 155},
  [22] = {.lex_state = 155},
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
  [55] = {.lex_state = 2},
  [56] = {.lex_state = 1},
  [57] = {.lex_state = 155},
  [58] = {.lex_state = 2},
  [59] = {.lex_state = 155},
  [60] = {.lex_state = 155},
  [61] = {.lex_state = 155},
  [62] = {.lex_state = 155},
  [63] = {.lex_state = 155},
  [64] = {.lex_state = 155},
  [65] = {.lex_state = 155},
  [66] = {.lex_state = 155},
  [67] = {.lex_state = 155},
  [68] = {.lex_state = 155},
  [69] = {.lex_state = 155},
  [70] = {.lex_state = 2},
  [71] = {.lex_state = 6},
  [72] = {.lex_state = 6},
  [73] = {.lex_state = 1},
  [74] = {.lex_state = 1},
  [75] = {.lex_state = 6},
  [76] = {.lex_state = 6},
  [77] = {.lex_state = 1},
  [78] = {.lex_state = 1},
  [79] = {.lex_state = 1},
  [80] = {.lex_state = 1},
  [81] = {.lex_state = 0},
  [82] = {.lex_state = 0},
  [83] = {.lex_state = 1},
  [84] = {.lex_state = 1},
  [85] = {.lex_state = 3},
  [86] = {.lex_state = 1},
  [87] = {.lex_state = 1},
  [88] = {.lex_state = 6},
  [89] = {.lex_state = 1},
  [90] = {.lex_state = 1},
  [91] = {.lex_state = 1},
  [92] = {.lex_state = 1},
  [93] = {.lex_state = 1},
  [94] = {.lex_state = 0},
  [95] = {.lex_state = 1},
  [96] = {.lex_state = 0},
  [97] = {.lex_state = 1},
  [98] = {.lex_state = 1},
  [99] = {.lex_state = 1},
  [100] = {.lex_state = 1},
  [101] = {.lex_state = 1},
  [102] = {.lex_state = 1},
  [103] = {.lex_state = 0},
  [104] = {.lex_state = 9},
  [105] = {.lex_state = 0},
  [106] = {.lex_state = 1},
  [107] = {.lex_state = 1},
  [108] = {.lex_state = 1},
  [109] = {.lex_state = 0},
  [110] = {.lex_state = 1},
  [111] = {.lex_state = 1},
  [112] = {.lex_state = 0},
  [113] = {.lex_state = 44},
  [114] = {.lex_state = 4},
  [115] = {.lex_state = 0},
  [116] = {.lex_state = 0},
  [117] = {.lex_state = 1},
  [118] = {.lex_state = 0},
  [119] = {.lex_state = 1},
  [120] = {.lex_state = 0},
  [121] = {.lex_state = 0},
  [122] = {.lex_state = 0},
  [123] = {.lex_state = 1},
  [124] = {.lex_state = 1},
  [125] = {.lex_state = 0},
  [126] = {.lex_state = 0},
  [127] = {.lex_state = 1},
  [128] = {.lex_state = 1},
  [129] = {.lex_state = 0},
  [130] = {.lex_state = 3},
  [131] = {.lex_state = 0},
  [132] = {.lex_state = 1},
  [133] = {.lex_state = 0},
  [134] = {.lex_state = 1},
  [135] = {.lex_state = 0},
  [136] = {.lex_state = 0},
  [137] = {.lex_state = 1},
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
  [154] = {.lex_state = 1},
  [155] = {.lex_state = 0},
  [156] = {.lex_state = 0},
  [157] = {.lex_state = 0},
  [158] = {.lex_state = 0},
  [159] = {.lex_state = 0},
  [160] = {.lex_state = 0},
  [161] = {.lex_state = 0},
  [162] = {.lex_state = 0},
  [163] = {.lex_state = 0},
  [164] = {.lex_state = 0},
  [165] = {.lex_state = 0},
  [166] = {.lex_state = 0},
  [167] = {.lex_state = 1},
  [168] = {.lex_state = 0},
  [169] = {.lex_state = 0},
  [170] = {.lex_state = 0},
  [171] = {.lex_state = 0},
  [172] = {.lex_state = 44},
  [173] = {.lex_state = 0},
  [174] = {.lex_state = 0},
  [175] = {.lex_state = 0},
  [176] = {.lex_state = 0},
  [177] = {.lex_state = 0},
  [178] = {.lex_state = 0},
  [179] = {.lex_state = 0},
  [180] = {.lex_state = 0},
  [181] = {.lex_state = 0},
  [182] = {.lex_state = 1},
  [183] = {.lex_state = 0},
  [184] = {.lex_state = 0},
  [185] = {.lex_state = 0},
  [186] = {.lex_state = 0},
  [187] = {.lex_state = 0},
  [188] = {.lex_state = 0},
  [189] = {.lex_state = 0},
  [190] = {.lex_state = 0},
  [191] = {.lex_state = 0},
  [192] = {.lex_state = 0},
  [193] = {.lex_state = 0},
  [194] = {.lex_state = 0},
  [195] = {.lex_state = 1},
  [196] = {.lex_state = 0},
  [197] = {.lex_state = 0},
  [198] = {.lex_state = 0},
  [199] = {.lex_state = 0},
  [200] = {.lex_state = 0},
  [201] = {.lex_state = 1},
  [202] = {.lex_state = 0},
  [203] = {.lex_state = 0},
  [204] = {.lex_state = 0},
  [205] = {.lex_state = 0},
  [206] = {.lex_state = 0},
  [207] = {.lex_state = 0},
  [208] = {.lex_state = 0},
  [209] = {.lex_state = 0},
  [210] = {.lex_state = 0},
  [211] = {.lex_state = 0},
  [212] = {.lex_state = 0},
  [213] = {.lex_state = 1},
  [214] = {.lex_state = 0},
  [215] = {.lex_state = 0},
  [216] = {.lex_state = 155},
  [217] = {.lex_state = 0},
  [218] = {.lex_state = 0},
  [219] = {.lex_state = 0},
  [220] = {.lex_state = 0},
  [221] = {.lex_state = 0},
  [222] = {.lex_state = 0},
  [223] = {.lex_state = 0},
  [224] = {.lex_state = 0},
  [225] = {.lex_state = 0},
  [226] = {.lex_state = 0},
  [227] = {.lex_state = 0},
  [228] = {.lex_state = 0},
  [229] = {.lex_state = 0},
  [230] = {.lex_state = 0},
  [231] = {.lex_state = 0},
  [232] = {.lex_state = 0},
  [233] = {.lex_state = 0},
  [234] = {.lex_state = 0},
  [235] = {.lex_state = 1},
  [236] = {.lex_state = 1},
  [237] = {.lex_state = 155},
  [238] = {.lex_state = 155},
  [239] = {.lex_state = 0},
  [240] = {.lex_state = 155},
  [241] = {.lex_state = 155},
  [242] = {.lex_state = 155},
  [243] = {.lex_state = 155},
  [244] = {.lex_state = 0},
  [245] = {.lex_state = 0},
  [246] = {.lex_state = 155},
  [247] = {.lex_state = 1},
  [248] = {.lex_state = 155},
  [249] = {.lex_state = 1},
  [250] = {.lex_state = 0},
  [251] = {.lex_state = 0},
  [252] = {.lex_state = 0},
  [253] = {.lex_state = 0},
  [254] = {.lex_state = 155},
  [255] = {.lex_state = 0},
  [256] = {.lex_state = 0},
  [257] = {.lex_state = 1},
  [258] = {.lex_state = 0},
  [259] = {.lex_state = 155},
  [260] = {.lex_state = 155},
  [261] = {.lex_state = 155},
  [262] = {.lex_state = 155},
  [263] = {.lex_state = 155},
  [264] = {.lex_state = 155},
  [265] = {.lex_state = 160},
  [266] = {.lex_state = 155},
  [267] = {.lex_state = 0},
  [268] = {.lex_state = 0},
  [269] = {.lex_state = 0},
  [270] = {.lex_state = 0},
  [271] = {.lex_state = 155},
  [272] = {.lex_state = 0},
  [273] = {.lex_state = 155},
  [274] = {.lex_state = 155},
  [275] = {.lex_state = 155},
  [276] = {.lex_state = 155},
  [277] = {.lex_state = 155},
  [278] = {.lex_state = 155},
  [279] = {.lex_state = 155},
  [280] = {.lex_state = 155},
  [281] = {.lex_state = 0},
  [282] = {.lex_state = 155},
  [283] = {.lex_state = 155},
  [284] = {.lex_state = 1},
  [285] = {.lex_state = 155},
  [286] = {.lex_state = 1},
  [287] = {.lex_state = 1},
  [288] = {.lex_state = 0},
  [289] = {.lex_state = 155},
  [290] = {.lex_state = 155},
  [291] = {.lex_state = 0},
  [292] = {.lex_state = 0},
  [293] = {.lex_state = 155},
  [294] = {.lex_state = 155},
  [295] = {.lex_state = 0},
  [296] = {.lex_state = 155},
  [297] = {.lex_state = 155},
  [298] = {.lex_state = 155},
  [299] = {.lex_state = 155},
};

static uint16_t ts_parse_table[LARGE_STATE_COUNT][SYMBOL_COUNT] = {
  [0] = {
    [ts_builtin_sym_end] = ACTIONS(1),
    [aux_sym__skipped_lines_token1] = ACTIONS(1),
    [aux_sym__skipped_lines_token3] = ACTIONS(1),
    [anon_sym_COLON] = ACTIONS(1),
    [aux_sym__skipped_lines_token4] = ACTIONS(1),
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
    [sym_account] = ACTIONS(1),
  },
  [1] = {
    [sym_beancount_file] = STATE(281),
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
    [aux_sym__skipped_lines_token1] = ACTIONS(5),
    [aux_sym__skipped_lines_token3] = ACTIONS(7),
    [anon_sym_COLON] = ACTIONS(5),
    [aux_sym__skipped_lines_token4] = ACTIONS(9),
    [anon_sym_include] = ACTIONS(11),
    [anon_sym_option] = ACTIONS(13),
    [anon_sym_plugin] = ACTIONS(15),
    [anon_sym_pushtag] = ACTIONS(17),
    [anon_sym_poptag] = ACTIONS(19),
    [anon_sym_pushmeta] = ACTIONS(21),
    [anon_sym_popmeta] = ACTIONS(23),
    [sym_date] = ACTIONS(25),
  },
};

static uint16_t ts_small_parse_table[] = {
  [0] = 13,
    ACTIONS(27), 1,
      ts_builtin_sym_end,
    ACTIONS(32), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(35), 1,
      aux_sym__skipped_lines_token4,
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
    ACTIONS(29), 2,
      aux_sym__skipped_lines_token1,
      anon_sym_COLON,
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
      aux_sym__skipped_lines_token4,
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
      aux_sym__skipped_lines_token3,
    ACTIONS(5), 2,
      aux_sym__skipped_lines_token1,
      anon_sym_COLON,
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
  [126] = 17,
    ACTIONS(66), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(68), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(70), 1,
      aux_sym_metadata_token1,
    ACTIONS(73), 1,
      anon_sym_LBRACE,
    ACTIONS(75), 1,
      anon_sym_LBRACE_LBRACE,
    ACTIONS(77), 1,
      anon_sym_AT_AT,
    ACTIONS(79), 1,
      anon_sym_AT,
    ACTIONS(81), 1,
      anon_sym_LPAREN,
    ACTIONS(85), 1,
      sym_currency,
    ACTIONS(87), 1,
      sym_number,
    STATE(81), 1,
      sym_incomplete_amount,
    STATE(96), 1,
      sym_cost_spec,
    STATE(139), 1,
      sym_price_annotation,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(211), 1,
      sym_metadata,
    ACTIONS(83), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(78), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [182] = 17,
    ACTIONS(73), 1,
      anon_sym_LBRACE,
    ACTIONS(75), 1,
      anon_sym_LBRACE_LBRACE,
    ACTIONS(77), 1,
      anon_sym_AT_AT,
    ACTIONS(79), 1,
      anon_sym_AT,
    ACTIONS(81), 1,
      anon_sym_LPAREN,
    ACTIONS(85), 1,
      sym_currency,
    ACTIONS(87), 1,
      sym_number,
    ACTIONS(89), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(91), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(93), 1,
      aux_sym_metadata_token1,
    STATE(82), 1,
      sym_incomplete_amount,
    STATE(105), 1,
      sym_cost_spec,
    STATE(129), 1,
      sym_price_annotation,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(208), 1,
      sym_metadata,
    ACTIONS(83), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(78), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [238] = 11,
    ACTIONS(96), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(100), 1,
      anon_sym_LPAREN,
    ACTIONS(104), 1,
      sym_bool,
    ACTIONS(108), 1,
      sym_number,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(283), 1,
      sym_metadata,
    ACTIONS(102), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(12), 2,
      sym_amount,
      aux_sym_custom_repeat1,
    ACTIONS(106), 3,
      sym_date,
      sym_string,
      sym_account,
    STATE(26), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [279] = 11,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(100), 1,
      anon_sym_LPAREN,
    ACTIONS(108), 1,
      sym_number,
    ACTIONS(110), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(112), 1,
      sym_bool,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(297), 1,
      sym_metadata,
    ACTIONS(102), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(6), 2,
      sym_amount,
      aux_sym_custom_repeat1,
    ACTIONS(114), 3,
      sym_date,
      sym_string,
      sym_account,
    STATE(26), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [320] = 9,
    ACTIONS(81), 1,
      anon_sym_LPAREN,
    ACTIONS(116), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(118), 1,
      aux_sym_metadata_token1,
    ACTIONS(124), 1,
      sym_number,
    ACTIONS(83), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    ACTIONS(120), 2,
      sym_bool,
      sym_currency,
    STATE(232), 2,
      sym__key_value_value,
      sym_amount,
    ACTIONS(122), 4,
      sym_date,
      sym_tag,
      sym_string,
      sym_account,
    STATE(111), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [357] = 8,
    ACTIONS(118), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(126), 1,
      anon_sym_LPAREN,
    ACTIONS(134), 1,
      sym_number,
    ACTIONS(128), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    ACTIONS(130), 2,
      sym_bool,
      sym_currency,
    STATE(263), 2,
      sym__key_value_value,
      sym_amount,
    ACTIONS(132), 4,
      sym_date,
      sym_tag,
      sym_string,
      sym_account,
    STATE(114), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [391] = 11,
    ACTIONS(126), 1,
      anon_sym_LPAREN,
    ACTIONS(136), 1,
      anon_sym_RBRACE,
    ACTIONS(140), 1,
      anon_sym_POUND,
    ACTIONS(142), 1,
      sym_currency,
    ACTIONS(144), 1,
      sym_number,
    STATE(176), 1,
      sym_cost_comp,
    STATE(191), 1,
      sym_compound_amount,
    STATE(247), 1,
      sym_cost_comp_list,
    ACTIONS(128), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    ACTIONS(138), 3,
      anon_sym_STAR,
      sym_date,
      sym_string,
    STATE(88), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [431] = 11,
    ACTIONS(126), 1,
      anon_sym_LPAREN,
    ACTIONS(136), 1,
      anon_sym_RBRACE_RBRACE,
    ACTIONS(140), 1,
      anon_sym_POUND,
    ACTIONS(142), 1,
      sym_currency,
    ACTIONS(144), 1,
      sym_number,
    STATE(176), 1,
      sym_cost_comp,
    STATE(191), 1,
      sym_compound_amount,
    STATE(240), 1,
      sym_cost_comp_list,
    ACTIONS(128), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    ACTIONS(138), 3,
      anon_sym_STAR,
      sym_date,
      sym_string,
    STATE(88), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [471] = 9,
    ACTIONS(146), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(148), 1,
      aux_sym_metadata_token1,
    ACTIONS(150), 1,
      anon_sym_LPAREN,
    ACTIONS(156), 1,
      sym_bool,
    ACTIONS(162), 1,
      sym_number,
    ACTIONS(153), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(12), 2,
      sym_amount,
      aux_sym_custom_repeat1,
    ACTIONS(159), 3,
      sym_date,
      sym_string,
      sym_account,
    STATE(26), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [506] = 9,
    ACTIONS(126), 1,
      anon_sym_LPAREN,
    ACTIONS(140), 1,
      anon_sym_POUND,
    ACTIONS(142), 1,
      sym_currency,
    ACTIONS(144), 1,
      sym_number,
    STATE(188), 1,
      sym_cost_comp,
    STATE(191), 1,
      sym_compound_amount,
    ACTIONS(128), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    ACTIONS(138), 3,
      anon_sym_STAR,
      sym_date,
      sym_string,
    STATE(88), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [540] = 1,
    ACTIONS(165), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [556] = 1,
    ACTIONS(167), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [572] = 13,
    ACTIONS(169), 1,
      aux_sym__skipped_lines_token1,
    ACTIONS(171), 1,
      anon_sym_balance,
    ACTIONS(173), 1,
      anon_sym_close,
    ACTIONS(175), 1,
      anon_sym_commodity,
    ACTIONS(177), 1,
      anon_sym_custom,
    ACTIONS(179), 1,
      anon_sym_document,
    ACTIONS(181), 1,
      anon_sym_event,
    ACTIONS(183), 1,
      anon_sym_note,
    ACTIONS(185), 1,
      anon_sym_open,
    ACTIONS(187), 1,
      anon_sym_pad,
    ACTIONS(189), 1,
      anon_sym_price,
    ACTIONS(191), 1,
      anon_sym_query,
    STATE(80), 1,
      sym_flag,
  [612] = 1,
    ACTIONS(193), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [628] = 1,
    ACTIONS(195), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [644] = 1,
    ACTIONS(197), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [660] = 3,
    ACTIONS(203), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(199), 4,
      aux_sym__skipped_lines_token3,
      sym_bool,
      sym_currency,
      sym_number,
    ACTIONS(201), 7,
      aux_sym_metadata_token1,
      anon_sym_LPAREN,
      anon_sym_DASH,
      anon_sym_PLUS,
      sym_date,
      sym_string,
      sym_account,
  [680] = 1,
    ACTIONS(205), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [696] = 1,
    ACTIONS(207), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [712] = 1,
    ACTIONS(209), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [728] = 1,
    ACTIONS(211), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [744] = 1,
    ACTIONS(213), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [760] = 5,
    ACTIONS(221), 1,
      sym_currency,
    ACTIONS(203), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(219), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    ACTIONS(215), 3,
      aux_sym__skipped_lines_token3,
      sym_bool,
      sym_number,
    ACTIONS(217), 5,
      aux_sym_metadata_token1,
      anon_sym_LPAREN,
      sym_date,
      sym_string,
      sym_account,
  [784] = 1,
    ACTIONS(223), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [800] = 1,
    ACTIONS(225), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [816] = 1,
    ACTIONS(227), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [832] = 1,
    ACTIONS(229), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [848] = 1,
    ACTIONS(231), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [864] = 1,
    ACTIONS(233), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [880] = 1,
    ACTIONS(235), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [896] = 1,
    ACTIONS(237), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [912] = 1,
    ACTIONS(239), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [928] = 1,
    ACTIONS(241), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [944] = 1,
    ACTIONS(243), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [960] = 1,
    ACTIONS(245), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [976] = 1,
    ACTIONS(247), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [992] = 1,
    ACTIONS(249), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1008] = 1,
    ACTIONS(251), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1024] = 1,
    ACTIONS(253), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1040] = 1,
    ACTIONS(255), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1056] = 1,
    ACTIONS(257), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1072] = 1,
    ACTIONS(259), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1088] = 1,
    ACTIONS(261), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1104] = 1,
    ACTIONS(263), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1120] = 1,
    ACTIONS(265), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1136] = 1,
    ACTIONS(267), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1152] = 1,
    ACTIONS(269), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1168] = 1,
    ACTIONS(271), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1184] = 1,
    ACTIONS(273), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1200] = 1,
    ACTIONS(275), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1216] = 1,
    ACTIONS(277), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1232] = 2,
    ACTIONS(199), 4,
      aux_sym__skipped_lines_token3,
      sym_bool,
      sym_currency,
      sym_number,
    ACTIONS(201), 9,
      aux_sym_metadata_token1,
      anon_sym_STAR,
      anon_sym_LPAREN,
      anon_sym_DASH,
      anon_sym_PLUS,
      anon_sym_SLASH,
      sym_date,
      sym_string,
      sym_account,
  [1250] = 8,
    ACTIONS(81), 1,
      anon_sym_LPAREN,
    ACTIONS(85), 1,
      sym_currency,
    ACTIONS(87), 1,
      sym_number,
    ACTIONS(279), 1,
      aux_sym__skipped_lines_token3,
    STATE(184), 1,
      sym_incomplete_amount,
    ACTIONS(83), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    ACTIONS(281), 2,
      aux_sym__skipped_lines_token4,
      aux_sym_metadata_token1,
    STATE(78), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1280] = 1,
    ACTIONS(283), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1296] = 2,
    ACTIONS(285), 4,
      aux_sym__skipped_lines_token3,
      sym_bool,
      sym_currency,
      sym_number,
    ACTIONS(287), 9,
      aux_sym_metadata_token1,
      anon_sym_STAR,
      anon_sym_LPAREN,
      anon_sym_DASH,
      anon_sym_PLUS,
      anon_sym_SLASH,
      sym_date,
      sym_string,
      sym_account,
  [1314] = 1,
    ACTIONS(289), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1330] = 1,
    ACTIONS(291), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1346] = 1,
    ACTIONS(293), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1362] = 1,
    ACTIONS(295), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1378] = 1,
    ACTIONS(297), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1394] = 1,
    ACTIONS(299), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1410] = 1,
    ACTIONS(301), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1426] = 1,
    ACTIONS(303), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1442] = 1,
    ACTIONS(305), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1458] = 1,
    ACTIONS(307), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1474] = 1,
    ACTIONS(309), 13,
      ts_builtin_sym_end,
      aux_sym__skipped_lines_token1,
      aux_sym__skipped_lines_token3,
      anon_sym_COLON,
      aux_sym__skipped_lines_token4,
      anon_sym_include,
      anon_sym_option,
      anon_sym_plugin,
      anon_sym_pushtag,
      anon_sym_poptag,
      anon_sym_pushmeta,
      anon_sym_popmeta,
      sym_date,
  [1490] = 2,
    ACTIONS(311), 4,
      aux_sym__skipped_lines_token3,
      sym_bool,
      sym_currency,
      sym_number,
    ACTIONS(313), 9,
      aux_sym_metadata_token1,
      anon_sym_STAR,
      anon_sym_LPAREN,
      anon_sym_DASH,
      anon_sym_PLUS,
      anon_sym_SLASH,
      sym_date,
      sym_string,
      sym_account,
  [1508] = 2,
    ACTIONS(285), 1,
      anon_sym_RBRACE,
    ACTIONS(287), 11,
      aux_sym__skipped_lines_token3,
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
  [1525] = 2,
    ACTIONS(311), 1,
      anon_sym_RBRACE,
    ACTIONS(313), 11,
      aux_sym__skipped_lines_token3,
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
  [1542] = 3,
    ACTIONS(315), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(199), 3,
      aux_sym__skipped_lines_token3,
      anon_sym_LBRACE,
      anon_sym_AT,
    ACTIONS(201), 7,
      aux_sym__skipped_lines_token4,
      aux_sym_metadata_token1,
      anon_sym_LBRACE_LBRACE,
      anon_sym_AT_AT,
      anon_sym_DASH,
      anon_sym_PLUS,
      sym_currency,
  [1561] = 2,
    ACTIONS(199), 3,
      aux_sym__skipped_lines_token3,
      anon_sym_LBRACE,
      anon_sym_AT,
    ACTIONS(201), 9,
      aux_sym__skipped_lines_token4,
      aux_sym_metadata_token1,
      anon_sym_LBRACE_LBRACE,
      anon_sym_STAR,
      anon_sym_AT_AT,
      anon_sym_DASH,
      anon_sym_PLUS,
      anon_sym_SLASH,
      sym_currency,
  [1578] = 2,
    ACTIONS(199), 1,
      anon_sym_RBRACE,
    ACTIONS(201), 11,
      aux_sym__skipped_lines_token3,
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
  [1595] = 3,
    ACTIONS(199), 1,
      anon_sym_RBRACE,
    ACTIONS(317), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(201), 9,
      aux_sym__skipped_lines_token3,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
      anon_sym_POUND,
      anon_sym_TILDE,
      anon_sym_RPAREN,
      anon_sym_DASH,
      anon_sym_PLUS,
      sym_currency,
  [1614] = 2,
    ACTIONS(285), 3,
      aux_sym__skipped_lines_token3,
      anon_sym_LBRACE,
      anon_sym_AT,
    ACTIONS(287), 9,
      aux_sym__skipped_lines_token4,
      aux_sym_metadata_token1,
      anon_sym_LBRACE_LBRACE,
      anon_sym_STAR,
      anon_sym_AT_AT,
      anon_sym_DASH,
      anon_sym_PLUS,
      anon_sym_SLASH,
      sym_currency,
  [1631] = 5,
    ACTIONS(325), 1,
      sym_currency,
    ACTIONS(315), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(323), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    ACTIONS(319), 3,
      aux_sym__skipped_lines_token3,
      anon_sym_LBRACE,
      anon_sym_AT,
    ACTIONS(321), 4,
      aux_sym__skipped_lines_token4,
      aux_sym_metadata_token1,
      anon_sym_LBRACE_LBRACE,
      anon_sym_AT_AT,
  [1654] = 2,
    ACTIONS(311), 3,
      aux_sym__skipped_lines_token3,
      anon_sym_LBRACE,
      anon_sym_AT,
    ACTIONS(313), 9,
      aux_sym__skipped_lines_token4,
      aux_sym_metadata_token1,
      anon_sym_LBRACE_LBRACE,
      anon_sym_STAR,
      anon_sym_AT_AT,
      anon_sym_DASH,
      anon_sym_PLUS,
      anon_sym_SLASH,
      sym_currency,
  [1671] = 10,
    ACTIONS(327), 1,
      aux_sym_metadata_token1,
    ACTIONS(331), 1,
      sym_string,
    STATE(83), 1,
      sym_txn_strings,
    STATE(116), 1,
      sym_tags_and_links,
    STATE(132), 1,
      aux_sym_tags_and_links_repeat1,
    STATE(151), 1,
      sym_metadata,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(276), 1,
      sym_postings,
    ACTIONS(329), 2,
      sym_tag,
      sym_link,
    STATE(146), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [1704] = 11,
    ACTIONS(73), 1,
      anon_sym_LBRACE,
    ACTIONS(75), 1,
      anon_sym_LBRACE_LBRACE,
    ACTIONS(77), 1,
      anon_sym_AT_AT,
    ACTIONS(79), 1,
      anon_sym_AT,
    ACTIONS(333), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(335), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(337), 1,
      aux_sym_metadata_token1,
    STATE(103), 1,
      sym_cost_spec,
    STATE(125), 1,
      sym_price_annotation,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(202), 1,
      sym_metadata,
  [1738] = 11,
    ACTIONS(73), 1,
      anon_sym_LBRACE,
    ACTIONS(75), 1,
      anon_sym_LBRACE_LBRACE,
    ACTIONS(77), 1,
      anon_sym_AT_AT,
    ACTIONS(79), 1,
      anon_sym_AT,
    ACTIONS(340), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(342), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(344), 1,
      aux_sym_metadata_token1,
    STATE(94), 1,
      sym_cost_spec,
    STATE(136), 1,
      sym_price_annotation,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(234), 1,
      sym_metadata,
  [1772] = 8,
    ACTIONS(327), 1,
      aux_sym_metadata_token1,
    STATE(115), 1,
      sym_tags_and_links,
    STATE(132), 1,
      aux_sym_tags_and_links_repeat1,
    STATE(180), 1,
      sym_metadata,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(289), 1,
      sym_postings,
    ACTIONS(329), 2,
      sym_tag,
      sym_link,
    STATE(146), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [1799] = 5,
    ACTIONS(126), 1,
      anon_sym_LPAREN,
    ACTIONS(347), 1,
      sym_number,
    ACTIONS(128), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(166), 2,
      sym_amount,
      sym_amount_with_tolerance,
    STATE(117), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1820] = 2,
    ACTIONS(349), 3,
      aux_sym__skipped_lines_token3,
      sym_bool,
      sym_number,
    ACTIONS(351), 7,
      aux_sym_metadata_token1,
      anon_sym_LPAREN,
      anon_sym_DASH,
      anon_sym_PLUS,
      sym_date,
      sym_string,
      sym_account,
  [1835] = 5,
    ACTIONS(126), 1,
      anon_sym_LPAREN,
    ACTIONS(353), 1,
      sym_number,
    STATE(161), 1,
      sym_amount,
    ACTIONS(128), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(128), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1855] = 5,
    ACTIONS(126), 1,
      anon_sym_LPAREN,
    ACTIONS(355), 1,
      sym_currency,
    ACTIONS(357), 1,
      sym_number,
    ACTIONS(128), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(137), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1875] = 6,
    ACTIONS(359), 1,
      anon_sym_RBRACE,
    ACTIONS(363), 1,
      anon_sym_POUND,
    ACTIONS(367), 1,
      sym_currency,
    ACTIONS(317), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(361), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
    ACTIONS(365), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [1897] = 5,
    ACTIONS(126), 1,
      anon_sym_LPAREN,
    ACTIONS(369), 1,
      sym_currency,
    ACTIONS(371), 1,
      sym_number,
    ACTIONS(128), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(119), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1917] = 4,
    ACTIONS(126), 1,
      anon_sym_LPAREN,
    ACTIONS(373), 1,
      sym_number,
    ACTIONS(128), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(75), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1934] = 4,
    ACTIONS(126), 1,
      anon_sym_LPAREN,
    ACTIONS(375), 1,
      sym_number,
    ACTIONS(128), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(72), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1951] = 4,
    ACTIONS(126), 1,
      anon_sym_LPAREN,
    ACTIONS(377), 1,
      sym_number,
    ACTIONS(128), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(76), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1968] = 4,
    ACTIONS(126), 1,
      anon_sym_LPAREN,
    ACTIONS(379), 1,
      sym_number,
    ACTIONS(128), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(141), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [1985] = 8,
    ACTIONS(77), 1,
      anon_sym_AT_AT,
    ACTIONS(79), 1,
      anon_sym_AT,
    ACTIONS(381), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(383), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(385), 1,
      aux_sym_metadata_token1,
    STATE(126), 1,
      sym_price_annotation,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(207), 1,
      sym_metadata,
  [2010] = 4,
    ACTIONS(81), 1,
      anon_sym_LPAREN,
    ACTIONS(388), 1,
      sym_number,
    ACTIONS(83), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(73), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2027] = 8,
    ACTIONS(77), 1,
      anon_sym_AT_AT,
    ACTIONS(79), 1,
      anon_sym_AT,
    ACTIONS(390), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(392), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(394), 1,
      aux_sym_metadata_token1,
    STATE(118), 1,
      sym_price_annotation,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(200), 1,
      sym_metadata,
  [2052] = 4,
    ACTIONS(126), 1,
      anon_sym_LPAREN,
    ACTIONS(397), 1,
      sym_number,
    ACTIONS(128), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(134), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2069] = 4,
    ACTIONS(81), 1,
      anon_sym_LPAREN,
    ACTIONS(399), 1,
      sym_number,
    ACTIONS(83), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(74), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2086] = 4,
    ACTIONS(81), 1,
      anon_sym_LPAREN,
    ACTIONS(401), 1,
      sym_number,
    ACTIONS(83), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(79), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2103] = 7,
    ACTIONS(403), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(405), 1,
      aux_sym_metadata_token1,
    STATE(132), 1,
      aux_sym_tags_and_links_repeat1,
    STATE(145), 1,
      sym_tags_and_links,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(282), 1,
      sym_metadata,
    ACTIONS(329), 2,
      sym_tag,
      sym_link,
  [2126] = 4,
    ACTIONS(126), 1,
      anon_sym_LPAREN,
    ACTIONS(407), 1,
      sym_number,
    ACTIONS(128), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(123), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2143] = 4,
    ACTIONS(100), 1,
      anon_sym_LPAREN,
    ACTIONS(409), 1,
      sym_number,
    ACTIONS(102), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(70), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2160] = 8,
    ACTIONS(77), 1,
      anon_sym_AT_AT,
    ACTIONS(79), 1,
      anon_sym_AT,
    ACTIONS(411), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(413), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(415), 1,
      aux_sym_metadata_token1,
    STATE(140), 1,
      sym_price_annotation,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(224), 1,
      sym_metadata,
  [2185] = 7,
    ACTIONS(418), 1,
      aux_sym__skipped_lines_token1,
    ACTIONS(420), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(422), 1,
      sym_key,
    ACTIONS(426), 1,
      sym_account,
    STATE(203), 1,
      sym_key_value,
    STATE(295), 1,
      sym_flag,
    ACTIONS(424), 2,
      sym_tag,
      sym_link,
  [2208] = 8,
    ACTIONS(77), 1,
      anon_sym_AT_AT,
    ACTIONS(79), 1,
      anon_sym_AT,
    ACTIONS(428), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(430), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(432), 1,
      aux_sym_metadata_token1,
    STATE(120), 1,
      sym_price_annotation,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(231), 1,
      sym_metadata,
  [2233] = 4,
    ACTIONS(100), 1,
      anon_sym_LPAREN,
    ACTIONS(435), 1,
      sym_number,
    ACTIONS(102), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(55), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2250] = 4,
    ACTIONS(126), 1,
      anon_sym_LPAREN,
    ACTIONS(437), 1,
      sym_number,
    ACTIONS(128), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(124), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2267] = 4,
    ACTIONS(100), 1,
      anon_sym_LPAREN,
    ACTIONS(439), 1,
      sym_number,
    ACTIONS(102), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
    STATE(20), 4,
      sym__num_expr,
      sym__paren_num_expr,
      sym_unary_num_expr,
      sym_binary_num_expr,
  [2284] = 2,
    ACTIONS(441), 3,
      aux_sym__skipped_lines_token3,
      anon_sym_LBRACE,
      anon_sym_AT,
    ACTIONS(443), 4,
      aux_sym__skipped_lines_token4,
      aux_sym_metadata_token1,
      anon_sym_LBRACE_LBRACE,
      anon_sym_AT_AT,
  [2296] = 7,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(445), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(447), 1,
      sym_string,
    ACTIONS(449), 1,
      sym_currency,
    STATE(131), 1,
      sym_currency_list,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(296), 1,
      sym_metadata,
  [2318] = 5,
    ACTIONS(451), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(453), 1,
      aux_sym_metadata_token1,
    ACTIONS(455), 1,
      sym_currency,
    ACTIONS(315), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(323), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2336] = 2,
    ACTIONS(319), 3,
      aux_sym__skipped_lines_token3,
      anon_sym_LBRACE,
      anon_sym_AT,
    ACTIONS(321), 4,
      aux_sym__skipped_lines_token4,
      aux_sym_metadata_token1,
      anon_sym_LBRACE_LBRACE,
      anon_sym_AT_AT,
  [2348] = 6,
    ACTIONS(418), 1,
      aux_sym__skipped_lines_token1,
    ACTIONS(420), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(422), 1,
      sym_key,
    ACTIONS(426), 1,
      sym_account,
    STATE(203), 1,
      sym_key_value,
    STATE(295), 1,
      sym_flag,
  [2367] = 4,
    ACTIONS(453), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(457), 1,
      sym_currency,
    ACTIONS(317), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(365), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2382] = 5,
    ACTIONS(459), 1,
      aux_sym_metadata_token1,
    STATE(170), 1,
      sym_metadata,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(262), 1,
      sym_postings,
    STATE(146), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [2399] = 5,
    ACTIONS(459), 1,
      aux_sym_metadata_token1,
    STATE(178), 1,
      sym_metadata,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(290), 1,
      sym_postings,
    STATE(146), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [2416] = 4,
    ACTIONS(455), 1,
      sym_currency,
    ACTIONS(461), 1,
      anon_sym_TILDE,
    ACTIONS(317), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(365), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2431] = 5,
    ACTIONS(463), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(465), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(467), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(221), 1,
      sym_metadata,
  [2447] = 3,
    ACTIONS(470), 1,
      sym_currency,
    ACTIONS(317), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(365), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2459] = 5,
    ACTIONS(472), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(474), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(476), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(204), 1,
      sym_metadata,
  [2475] = 4,
    ACTIONS(479), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(483), 1,
      anon_sym_COMMA,
    STATE(121), 1,
      aux_sym_currency_list_repeat1,
    ACTIONS(481), 2,
      aux_sym_metadata_token1,
      sym_string,
  [2489] = 2,
    ACTIONS(486), 2,
      aux_sym__skipped_lines_token3,
      anon_sym_AT,
    ACTIONS(488), 3,
      aux_sym__skipped_lines_token4,
      aux_sym_metadata_token1,
      anon_sym_AT_AT,
  [2499] = 3,
    ACTIONS(490), 1,
      anon_sym_RPAREN,
    ACTIONS(317), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(365), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2511] = 3,
    ACTIONS(492), 1,
      sym_currency,
    ACTIONS(317), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(365), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2523] = 5,
    ACTIONS(494), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(496), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(498), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(227), 1,
      sym_metadata,
  [2539] = 5,
    ACTIONS(501), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(503), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(505), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(225), 1,
      sym_metadata,
  [2555] = 4,
    ACTIONS(508), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(510), 1,
      aux_sym_metadata_token1,
    STATE(127), 1,
      aux_sym_tags_and_links_repeat1,
    ACTIONS(513), 2,
      sym_tag,
      sym_link,
  [2569] = 3,
    ACTIONS(455), 1,
      sym_currency,
    ACTIONS(317), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(365), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2581] = 5,
    ACTIONS(516), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(518), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(520), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(197), 1,
      sym_metadata,
  [2597] = 1,
    ACTIONS(523), 5,
      aux_sym_metadata_token1,
      sym_tag,
      sym_link,
      sym_string,
      sym_account,
  [2605] = 5,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(525), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(527), 1,
      sym_string,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(275), 1,
      sym_metadata,
  [2621] = 4,
    ACTIONS(529), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(531), 1,
      aux_sym_metadata_token1,
    STATE(127), 1,
      aux_sym_tags_and_links_repeat1,
    ACTIONS(534), 2,
      sym_tag,
      sym_link,
  [2635] = 4,
    ACTIONS(536), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(540), 1,
      anon_sym_COMMA,
    STATE(121), 1,
      aux_sym_currency_list_repeat1,
    ACTIONS(538), 2,
      aux_sym_metadata_token1,
      sym_string,
  [2649] = 3,
    ACTIONS(542), 1,
      anon_sym_RPAREN,
    ACTIONS(317), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(365), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2661] = 4,
    ACTIONS(540), 1,
      anon_sym_COMMA,
    ACTIONS(544), 1,
      aux_sym__skipped_lines_token3,
    STATE(133), 1,
      aux_sym_currency_list_repeat1,
    ACTIONS(546), 2,
      aux_sym_metadata_token1,
      sym_string,
  [2675] = 5,
    ACTIONS(548), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(550), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(552), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(196), 1,
      sym_metadata,
  [2691] = 3,
    ACTIONS(555), 1,
      sym_currency,
    ACTIONS(317), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(365), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2703] = 2,
    ACTIONS(557), 2,
      aux_sym__skipped_lines_token3,
      anon_sym_AT,
    ACTIONS(559), 3,
      aux_sym__skipped_lines_token4,
      aux_sym_metadata_token1,
      anon_sym_AT_AT,
  [2713] = 5,
    ACTIONS(561), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(563), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(565), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(205), 1,
      sym_metadata,
  [2729] = 5,
    ACTIONS(568), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(570), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(572), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(215), 1,
      sym_metadata,
  [2745] = 3,
    ACTIONS(575), 1,
      anon_sym_RPAREN,
    ACTIONS(317), 2,
      anon_sym_STAR,
      anon_sym_SLASH,
    ACTIONS(365), 2,
      anon_sym_DASH,
      anon_sym_PLUS,
  [2757] = 4,
    ACTIONS(577), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(579), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(226), 1,
      sym_metadata,
  [2770] = 4,
    ACTIONS(582), 1,
      anon_sym_RBRACE,
    ACTIONS(584), 1,
      anon_sym_RBRACE_RBRACE,
    ACTIONS(586), 1,
      anon_sym_COMMA,
    STATE(143), 1,
      aux_sym_cost_comp_list_repeat1,
  [2783] = 4,
    ACTIONS(589), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(591), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(206), 1,
      sym_metadata,
  [2796] = 4,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(594), 1,
      aux_sym__skipped_lines_token3,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(259), 1,
      sym_metadata,
  [2809] = 3,
    ACTIONS(596), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(598), 1,
      aux_sym_metadata_token1,
    STATE(173), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [2820] = 4,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(600), 1,
      aux_sym__skipped_lines_token3,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(280), 1,
      sym_metadata,
  [2833] = 4,
    ACTIONS(602), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(604), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(199), 1,
      sym_metadata,
  [2846] = 4,
    ACTIONS(607), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(609), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(198), 1,
      sym_metadata,
  [2859] = 4,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(612), 1,
      aux_sym__skipped_lines_token3,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(279), 1,
      sym_metadata,
  [2872] = 3,
    ACTIONS(598), 1,
      aux_sym_metadata_token1,
    STATE(294), 1,
      sym_postings,
    STATE(146), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [2883] = 4,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(614), 1,
      aux_sym__skipped_lines_token3,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(254), 1,
      sym_metadata,
  [2896] = 4,
    ACTIONS(616), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(618), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(210), 1,
      sym_metadata,
  [2909] = 2,
    ACTIONS(623), 1,
      sym_string,
    ACTIONS(621), 3,
      aux_sym_metadata_token1,
      sym_tag,
      sym_link,
  [2918] = 4,
    ACTIONS(625), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(627), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(230), 1,
      sym_metadata,
  [2931] = 4,
    ACTIONS(630), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(632), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(233), 1,
      sym_metadata,
  [2944] = 4,
    ACTIONS(635), 1,
      anon_sym_RBRACE,
    ACTIONS(637), 1,
      anon_sym_RBRACE_RBRACE,
    ACTIONS(639), 1,
      anon_sym_COMMA,
    STATE(143), 1,
      aux_sym_cost_comp_list_repeat1,
  [2957] = 4,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(641), 1,
      aux_sym__skipped_lines_token3,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(278), 1,
      sym_metadata,
  [2970] = 4,
    ACTIONS(643), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(645), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(218), 1,
      sym_metadata,
  [2983] = 4,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(648), 1,
      aux_sym__skipped_lines_token3,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(274), 1,
      sym_metadata,
  [2996] = 4,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(650), 1,
      aux_sym__skipped_lines_token3,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(273), 1,
      sym_metadata,
  [3009] = 4,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(652), 1,
      aux_sym__skipped_lines_token3,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(271), 1,
      sym_metadata,
  [3022] = 4,
    ACTIONS(654), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(656), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(229), 1,
      sym_metadata,
  [3035] = 4,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(659), 1,
      aux_sym__skipped_lines_token3,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(298), 1,
      sym_metadata,
  [3048] = 4,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(661), 1,
      aux_sym__skipped_lines_token3,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(299), 1,
      sym_metadata,
  [3061] = 4,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(663), 1,
      aux_sym__skipped_lines_token3,
    STATE(190), 1,
      aux_sym_metadata_repeat1,
    STATE(285), 1,
      sym_metadata,
  [3074] = 2,
    ACTIONS(508), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(665), 3,
      aux_sym_metadata_token1,
      sym_tag,
      sym_link,
  [3083] = 4,
    ACTIONS(667), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(669), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(223), 1,
      sym_metadata,
  [3096] = 4,
    ACTIONS(672), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(674), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(228), 1,
      sym_metadata,
  [3109] = 3,
    ACTIONS(598), 1,
      aux_sym_metadata_token1,
    STATE(242), 1,
      sym_postings,
    STATE(146), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [3120] = 4,
    ACTIONS(677), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(679), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(222), 1,
      sym_metadata,
  [3133] = 4,
    ACTIONS(418), 1,
      aux_sym__skipped_lines_token1,
    ACTIONS(420), 1,
      aux_sym__skipped_lines_token4,
    ACTIONS(426), 1,
      sym_account,
    STATE(295), 1,
      sym_flag,
  [3146] = 3,
    ACTIONS(682), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(684), 1,
      aux_sym_metadata_token1,
    STATE(173), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [3157] = 4,
    ACTIONS(687), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(689), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(219), 1,
      sym_metadata,
  [3170] = 4,
    ACTIONS(692), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(694), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(220), 1,
      sym_metadata,
  [3183] = 4,
    ACTIONS(639), 1,
      anon_sym_COMMA,
    ACTIONS(697), 1,
      anon_sym_RBRACE,
    ACTIONS(699), 1,
      anon_sym_RBRACE_RBRACE,
    STATE(157), 1,
      aux_sym_cost_comp_list_repeat1,
  [3196] = 4,
    ACTIONS(701), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(703), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(214), 1,
      sym_metadata,
  [3209] = 3,
    ACTIONS(598), 1,
      aux_sym_metadata_token1,
    STATE(266), 1,
      sym_postings,
    STATE(146), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [3220] = 4,
    ACTIONS(706), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(708), 1,
      aux_sym_metadata_token1,
    STATE(185), 1,
      aux_sym_metadata_repeat1,
    STATE(217), 1,
      sym_metadata,
  [3233] = 3,
    ACTIONS(598), 1,
      aux_sym_metadata_token1,
    STATE(264), 1,
      sym_postings,
    STATE(146), 2,
      sym_posting,
      aux_sym_postings_repeat1,
  [3244] = 2,
    ACTIONS(479), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(481), 3,
      aux_sym_metadata_token1,
      anon_sym_COMMA,
      sym_string,
  [3253] = 3,
    ACTIONS(422), 1,
      sym_key,
    STATE(203), 1,
      sym_key_value,
    ACTIONS(424), 2,
      sym_tag,
      sym_link,
  [3264] = 2,
    ACTIONS(711), 1,
      anon_sym_RBRACE,
    ACTIONS(713), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [3272] = 2,
    ACTIONS(715), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(717), 2,
      aux_sym__skipped_lines_token4,
      aux_sym_metadata_token1,
  [3280] = 3,
    ACTIONS(719), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(721), 1,
      aux_sym_metadata_token1,
    STATE(194), 1,
      aux_sym_metadata_repeat1,
  [3290] = 2,
    ACTIONS(724), 1,
      anon_sym_RBRACE,
    ACTIONS(726), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [3298] = 2,
    ACTIONS(728), 1,
      anon_sym_RBRACE,
    ACTIONS(730), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [3306] = 2,
    ACTIONS(582), 1,
      anon_sym_RBRACE,
    ACTIONS(584), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [3314] = 2,
    ACTIONS(732), 1,
      anon_sym_RBRACE,
    ACTIONS(734), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [3322] = 3,
    ACTIONS(98), 1,
      aux_sym_metadata_token1,
    ACTIONS(719), 1,
      aux_sym__skipped_lines_token3,
    STATE(194), 1,
      aux_sym_metadata_repeat1,
  [3332] = 2,
    ACTIONS(736), 1,
      anon_sym_RBRACE,
    ACTIONS(738), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [3340] = 2,
    ACTIONS(740), 1,
      anon_sym_RBRACE,
    ACTIONS(742), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [3348] = 2,
    ACTIONS(744), 1,
      anon_sym_RBRACE,
    ACTIONS(746), 2,
      anon_sym_RBRACE_RBRACE,
      anon_sym_COMMA,
  [3356] = 3,
    ACTIONS(748), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(750), 1,
      aux_sym_metadata_token1,
    STATE(194), 1,
      aux_sym_metadata_repeat1,
  [3366] = 1,
    ACTIONS(753), 3,
      aux_sym_metadata_token1,
      sym_tag,
      sym_link,
  [3372] = 2,
    ACTIONS(755), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(757), 1,
      aux_sym_metadata_token1,
  [3379] = 2,
    ACTIONS(759), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(761), 1,
      aux_sym_metadata_token1,
  [3386] = 2,
    ACTIONS(763), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(765), 1,
      aux_sym_metadata_token1,
  [3393] = 2,
    ACTIONS(767), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(769), 1,
      aux_sym_metadata_token1,
  [3400] = 2,
    ACTIONS(771), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(773), 1,
      aux_sym_metadata_token1,
  [3407] = 1,
    ACTIONS(424), 2,
      sym_tag,
      sym_link,
  [3412] = 2,
    ACTIONS(775), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(777), 1,
      aux_sym_metadata_token1,
  [3419] = 2,
    ACTIONS(748), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(779), 1,
      aux_sym_metadata_token1,
  [3426] = 2,
    ACTIONS(781), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(783), 1,
      aux_sym_metadata_token1,
  [3433] = 2,
    ACTIONS(785), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(787), 1,
      aux_sym_metadata_token1,
  [3440] = 2,
    ACTIONS(789), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(791), 1,
      aux_sym_metadata_token1,
  [3447] = 2,
    ACTIONS(793), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(795), 1,
      aux_sym_metadata_token1,
  [3454] = 2,
    ACTIONS(797), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(799), 1,
      aux_sym_metadata_token1,
  [3461] = 2,
    ACTIONS(682), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(801), 1,
      aux_sym_metadata_token1,
  [3468] = 2,
    ACTIONS(803), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(805), 1,
      aux_sym_metadata_token1,
  [3475] = 2,
    ACTIONS(807), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(809), 1,
      aux_sym_metadata_token1,
  [3482] = 2,
    ACTIONS(811), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(813), 1,
      aux_sym_metadata_token1,
  [3489] = 2,
    ACTIONS(815), 1,
      sym_key,
    STATE(243), 1,
      sym_key_value,
  [3496] = 2,
    ACTIONS(817), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(819), 1,
      aux_sym_metadata_token1,
  [3503] = 2,
    ACTIONS(821), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(823), 1,
      aux_sym_metadata_token1,
  [3510] = 2,
    ACTIONS(825), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(827), 1,
      sym_string,
  [3517] = 2,
    ACTIONS(829), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(831), 1,
      aux_sym_metadata_token1,
  [3524] = 2,
    ACTIONS(833), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(835), 1,
      aux_sym_metadata_token1,
  [3531] = 2,
    ACTIONS(837), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(839), 1,
      aux_sym_metadata_token1,
  [3538] = 2,
    ACTIONS(841), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(843), 1,
      aux_sym_metadata_token1,
  [3545] = 2,
    ACTIONS(845), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(847), 1,
      aux_sym_metadata_token1,
  [3552] = 2,
    ACTIONS(849), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(851), 1,
      aux_sym_metadata_token1,
  [3559] = 2,
    ACTIONS(853), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(855), 1,
      aux_sym_metadata_token1,
  [3566] = 2,
    ACTIONS(857), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(859), 1,
      aux_sym_metadata_token1,
  [3573] = 2,
    ACTIONS(861), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(863), 1,
      aux_sym_metadata_token1,
  [3580] = 2,
    ACTIONS(865), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(867), 1,
      aux_sym_metadata_token1,
  [3587] = 2,
    ACTIONS(869), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(871), 1,
      aux_sym_metadata_token1,
  [3594] = 2,
    ACTIONS(873), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(875), 1,
      aux_sym_metadata_token1,
  [3601] = 2,
    ACTIONS(877), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(879), 1,
      aux_sym_metadata_token1,
  [3608] = 2,
    ACTIONS(881), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(883), 1,
      aux_sym_metadata_token1,
  [3615] = 2,
    ACTIONS(885), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(887), 1,
      aux_sym_metadata_token1,
  [3622] = 2,
    ACTIONS(889), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(891), 1,
      aux_sym_metadata_token1,
  [3629] = 2,
    ACTIONS(893), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(895), 1,
      aux_sym_metadata_token1,
  [3636] = 2,
    ACTIONS(897), 1,
      aux_sym__skipped_lines_token3,
    ACTIONS(899), 1,
      aux_sym_metadata_token1,
  [3643] = 2,
    ACTIONS(422), 1,
      sym_key,
    STATE(203), 1,
      sym_key_value,
  [3650] = 1,
    ACTIONS(901), 1,
      sym_currency,
  [3654] = 1,
    ACTIONS(903), 1,
      aux_sym__skipped_lines_token3,
  [3658] = 1,
    ACTIONS(905), 1,
      aux_sym__skipped_lines_token3,
  [3662] = 1,
    ACTIONS(907), 1,
      sym_account,
  [3666] = 1,
    ACTIONS(909), 1,
      anon_sym_RBRACE_RBRACE,
  [3670] = 1,
    ACTIONS(911), 1,
      aux_sym__skipped_lines_token3,
  [3674] = 1,
    ACTIONS(913), 1,
      aux_sym__skipped_lines_token3,
  [3678] = 1,
    ACTIONS(915), 1,
      aux_sym__skipped_lines_token3,
  [3682] = 1,
    ACTIONS(917), 1,
      sym_string,
  [3686] = 1,
    ACTIONS(919), 1,
      sym_account,
  [3690] = 1,
    ACTIONS(351), 1,
      aux_sym__skipped_lines_token3,
  [3694] = 1,
    ACTIONS(909), 1,
      anon_sym_RBRACE,
  [3698] = 1,
    ACTIONS(921), 1,
      aux_sym__skipped_lines_token3,
  [3702] = 1,
    ACTIONS(923), 1,
      sym_currency,
  [3706] = 1,
    ACTIONS(925), 1,
      sym_string,
  [3710] = 1,
    ACTIONS(927), 1,
      sym_account,
  [3714] = 1,
    ACTIONS(929), 1,
      sym_string,
  [3718] = 1,
    ACTIONS(931), 1,
      sym_account,
  [3722] = 1,
    ACTIONS(933), 1,
      aux_sym__skipped_lines_token3,
  [3726] = 1,
    ACTIONS(935), 1,
      sym_account,
  [3730] = 1,
    ACTIONS(937), 1,
      sym_account,
  [3734] = 1,
    ACTIONS(939), 1,
      sym_currency,
  [3738] = 1,
    ACTIONS(941), 1,
      sym_string,
  [3742] = 1,
    ACTIONS(943), 1,
      aux_sym__skipped_lines_token3,
  [3746] = 1,
    ACTIONS(945), 1,
      aux_sym__skipped_lines_token3,
  [3750] = 1,
    ACTIONS(947), 1,
      aux_sym__skipped_lines_token3,
  [3754] = 1,
    ACTIONS(949), 1,
      aux_sym__skipped_lines_token3,
  [3758] = 1,
    ACTIONS(891), 1,
      aux_sym__skipped_lines_token3,
  [3762] = 1,
    ACTIONS(951), 1,
      aux_sym__skipped_lines_token3,
  [3766] = 1,
    ACTIONS(953), 1,
      aux_sym__skipped_lines_token2,
  [3770] = 1,
    ACTIONS(955), 1,
      aux_sym__skipped_lines_token3,
  [3774] = 1,
    ACTIONS(957), 1,
      sym_string,
  [3778] = 1,
    ACTIONS(959), 1,
      sym_string,
  [3782] = 1,
    ACTIONS(961), 1,
      sym_string,
  [3786] = 1,
    ACTIONS(963), 1,
      sym_account,
  [3790] = 1,
    ACTIONS(965), 1,
      aux_sym__skipped_lines_token3,
  [3794] = 1,
    ACTIONS(967), 1,
      sym_string,
  [3798] = 1,
    ACTIONS(969), 1,
      aux_sym__skipped_lines_token3,
  [3802] = 1,
    ACTIONS(971), 1,
      aux_sym__skipped_lines_token3,
  [3806] = 1,
    ACTIONS(973), 1,
      aux_sym__skipped_lines_token3,
  [3810] = 1,
    ACTIONS(975), 1,
      aux_sym__skipped_lines_token3,
  [3814] = 1,
    ACTIONS(977), 1,
      aux_sym__skipped_lines_token3,
  [3818] = 1,
    ACTIONS(979), 1,
      aux_sym__skipped_lines_token3,
  [3822] = 1,
    ACTIONS(981), 1,
      aux_sym__skipped_lines_token3,
  [3826] = 1,
    ACTIONS(983), 1,
      aux_sym__skipped_lines_token3,
  [3830] = 1,
    ACTIONS(985), 1,
      ts_builtin_sym_end,
  [3834] = 1,
    ACTIONS(987), 1,
      aux_sym__skipped_lines_token3,
  [3838] = 1,
    ACTIONS(989), 1,
      aux_sym__skipped_lines_token3,
  [3842] = 1,
    ACTIONS(991), 1,
      sym_key,
  [3846] = 1,
    ACTIONS(993), 1,
      aux_sym__skipped_lines_token3,
  [3850] = 1,
    ACTIONS(995), 1,
      sym_tag,
  [3854] = 1,
    ACTIONS(997), 1,
      sym_tag,
  [3858] = 1,
    ACTIONS(999), 1,
      sym_string,
  [3862] = 1,
    ACTIONS(1001), 1,
      aux_sym__skipped_lines_token3,
  [3866] = 1,
    ACTIONS(1003), 1,
      aux_sym__skipped_lines_token3,
  [3870] = 1,
    ACTIONS(1005), 1,
      sym_string,
  [3874] = 1,
    ACTIONS(1007), 1,
      sym_string,
  [3878] = 1,
    ACTIONS(1009), 1,
      aux_sym__skipped_lines_token3,
  [3882] = 1,
    ACTIONS(1011), 1,
      aux_sym__skipped_lines_token3,
  [3886] = 1,
    ACTIONS(1013), 1,
      sym_account,
  [3890] = 1,
    ACTIONS(1015), 1,
      aux_sym__skipped_lines_token3,
  [3894] = 1,
    ACTIONS(1017), 1,
      aux_sym__skipped_lines_token3,
  [3898] = 1,
    ACTIONS(1019), 1,
      aux_sym__skipped_lines_token3,
  [3902] = 1,
    ACTIONS(1021), 1,
      aux_sym__skipped_lines_token3,
};

static uint32_t ts_small_parse_table_map[] = {
  [SMALL_STATE(2)] = 0,
  [SMALL_STATE(3)] = 63,
  [SMALL_STATE(4)] = 126,
  [SMALL_STATE(5)] = 182,
  [SMALL_STATE(6)] = 238,
  [SMALL_STATE(7)] = 279,
  [SMALL_STATE(8)] = 320,
  [SMALL_STATE(9)] = 357,
  [SMALL_STATE(10)] = 391,
  [SMALL_STATE(11)] = 431,
  [SMALL_STATE(12)] = 471,
  [SMALL_STATE(13)] = 506,
  [SMALL_STATE(14)] = 540,
  [SMALL_STATE(15)] = 556,
  [SMALL_STATE(16)] = 572,
  [SMALL_STATE(17)] = 612,
  [SMALL_STATE(18)] = 628,
  [SMALL_STATE(19)] = 644,
  [SMALL_STATE(20)] = 660,
  [SMALL_STATE(21)] = 680,
  [SMALL_STATE(22)] = 696,
  [SMALL_STATE(23)] = 712,
  [SMALL_STATE(24)] = 728,
  [SMALL_STATE(25)] = 744,
  [SMALL_STATE(26)] = 760,
  [SMALL_STATE(27)] = 784,
  [SMALL_STATE(28)] = 800,
  [SMALL_STATE(29)] = 816,
  [SMALL_STATE(30)] = 832,
  [SMALL_STATE(31)] = 848,
  [SMALL_STATE(32)] = 864,
  [SMALL_STATE(33)] = 880,
  [SMALL_STATE(34)] = 896,
  [SMALL_STATE(35)] = 912,
  [SMALL_STATE(36)] = 928,
  [SMALL_STATE(37)] = 944,
  [SMALL_STATE(38)] = 960,
  [SMALL_STATE(39)] = 976,
  [SMALL_STATE(40)] = 992,
  [SMALL_STATE(41)] = 1008,
  [SMALL_STATE(42)] = 1024,
  [SMALL_STATE(43)] = 1040,
  [SMALL_STATE(44)] = 1056,
  [SMALL_STATE(45)] = 1072,
  [SMALL_STATE(46)] = 1088,
  [SMALL_STATE(47)] = 1104,
  [SMALL_STATE(48)] = 1120,
  [SMALL_STATE(49)] = 1136,
  [SMALL_STATE(50)] = 1152,
  [SMALL_STATE(51)] = 1168,
  [SMALL_STATE(52)] = 1184,
  [SMALL_STATE(53)] = 1200,
  [SMALL_STATE(54)] = 1216,
  [SMALL_STATE(55)] = 1232,
  [SMALL_STATE(56)] = 1250,
  [SMALL_STATE(57)] = 1280,
  [SMALL_STATE(58)] = 1296,
  [SMALL_STATE(59)] = 1314,
  [SMALL_STATE(60)] = 1330,
  [SMALL_STATE(61)] = 1346,
  [SMALL_STATE(62)] = 1362,
  [SMALL_STATE(63)] = 1378,
  [SMALL_STATE(64)] = 1394,
  [SMALL_STATE(65)] = 1410,
  [SMALL_STATE(66)] = 1426,
  [SMALL_STATE(67)] = 1442,
  [SMALL_STATE(68)] = 1458,
  [SMALL_STATE(69)] = 1474,
  [SMALL_STATE(70)] = 1490,
  [SMALL_STATE(71)] = 1508,
  [SMALL_STATE(72)] = 1525,
  [SMALL_STATE(73)] = 1542,
  [SMALL_STATE(74)] = 1561,
  [SMALL_STATE(75)] = 1578,
  [SMALL_STATE(76)] = 1595,
  [SMALL_STATE(77)] = 1614,
  [SMALL_STATE(78)] = 1631,
  [SMALL_STATE(79)] = 1654,
  [SMALL_STATE(80)] = 1671,
  [SMALL_STATE(81)] = 1704,
  [SMALL_STATE(82)] = 1738,
  [SMALL_STATE(83)] = 1772,
  [SMALL_STATE(84)] = 1799,
  [SMALL_STATE(85)] = 1820,
  [SMALL_STATE(86)] = 1835,
  [SMALL_STATE(87)] = 1855,
  [SMALL_STATE(88)] = 1875,
  [SMALL_STATE(89)] = 1897,
  [SMALL_STATE(90)] = 1917,
  [SMALL_STATE(91)] = 1934,
  [SMALL_STATE(92)] = 1951,
  [SMALL_STATE(93)] = 1968,
  [SMALL_STATE(94)] = 1985,
  [SMALL_STATE(95)] = 2010,
  [SMALL_STATE(96)] = 2027,
  [SMALL_STATE(97)] = 2052,
  [SMALL_STATE(98)] = 2069,
  [SMALL_STATE(99)] = 2086,
  [SMALL_STATE(100)] = 2103,
  [SMALL_STATE(101)] = 2126,
  [SMALL_STATE(102)] = 2143,
  [SMALL_STATE(103)] = 2160,
  [SMALL_STATE(104)] = 2185,
  [SMALL_STATE(105)] = 2208,
  [SMALL_STATE(106)] = 2233,
  [SMALL_STATE(107)] = 2250,
  [SMALL_STATE(108)] = 2267,
  [SMALL_STATE(109)] = 2284,
  [SMALL_STATE(110)] = 2296,
  [SMALL_STATE(111)] = 2318,
  [SMALL_STATE(112)] = 2336,
  [SMALL_STATE(113)] = 2348,
  [SMALL_STATE(114)] = 2367,
  [SMALL_STATE(115)] = 2382,
  [SMALL_STATE(116)] = 2399,
  [SMALL_STATE(117)] = 2416,
  [SMALL_STATE(118)] = 2431,
  [SMALL_STATE(119)] = 2447,
  [SMALL_STATE(120)] = 2459,
  [SMALL_STATE(121)] = 2475,
  [SMALL_STATE(122)] = 2489,
  [SMALL_STATE(123)] = 2499,
  [SMALL_STATE(124)] = 2511,
  [SMALL_STATE(125)] = 2523,
  [SMALL_STATE(126)] = 2539,
  [SMALL_STATE(127)] = 2555,
  [SMALL_STATE(128)] = 2569,
  [SMALL_STATE(129)] = 2581,
  [SMALL_STATE(130)] = 2597,
  [SMALL_STATE(131)] = 2605,
  [SMALL_STATE(132)] = 2621,
  [SMALL_STATE(133)] = 2635,
  [SMALL_STATE(134)] = 2649,
  [SMALL_STATE(135)] = 2661,
  [SMALL_STATE(136)] = 2675,
  [SMALL_STATE(137)] = 2691,
  [SMALL_STATE(138)] = 2703,
  [SMALL_STATE(139)] = 2713,
  [SMALL_STATE(140)] = 2729,
  [SMALL_STATE(141)] = 2745,
  [SMALL_STATE(142)] = 2757,
  [SMALL_STATE(143)] = 2770,
  [SMALL_STATE(144)] = 2783,
  [SMALL_STATE(145)] = 2796,
  [SMALL_STATE(146)] = 2809,
  [SMALL_STATE(147)] = 2820,
  [SMALL_STATE(148)] = 2833,
  [SMALL_STATE(149)] = 2846,
  [SMALL_STATE(150)] = 2859,
  [SMALL_STATE(151)] = 2872,
  [SMALL_STATE(152)] = 2883,
  [SMALL_STATE(153)] = 2896,
  [SMALL_STATE(154)] = 2909,
  [SMALL_STATE(155)] = 2918,
  [SMALL_STATE(156)] = 2931,
  [SMALL_STATE(157)] = 2944,
  [SMALL_STATE(158)] = 2957,
  [SMALL_STATE(159)] = 2970,
  [SMALL_STATE(160)] = 2983,
  [SMALL_STATE(161)] = 2996,
  [SMALL_STATE(162)] = 3009,
  [SMALL_STATE(163)] = 3022,
  [SMALL_STATE(164)] = 3035,
  [SMALL_STATE(165)] = 3048,
  [SMALL_STATE(166)] = 3061,
  [SMALL_STATE(167)] = 3074,
  [SMALL_STATE(168)] = 3083,
  [SMALL_STATE(169)] = 3096,
  [SMALL_STATE(170)] = 3109,
  [SMALL_STATE(171)] = 3120,
  [SMALL_STATE(172)] = 3133,
  [SMALL_STATE(173)] = 3146,
  [SMALL_STATE(174)] = 3157,
  [SMALL_STATE(175)] = 3170,
  [SMALL_STATE(176)] = 3183,
  [SMALL_STATE(177)] = 3196,
  [SMALL_STATE(178)] = 3209,
  [SMALL_STATE(179)] = 3220,
  [SMALL_STATE(180)] = 3233,
  [SMALL_STATE(181)] = 3244,
  [SMALL_STATE(182)] = 3253,
  [SMALL_STATE(183)] = 3264,
  [SMALL_STATE(184)] = 3272,
  [SMALL_STATE(185)] = 3280,
  [SMALL_STATE(186)] = 3290,
  [SMALL_STATE(187)] = 3298,
  [SMALL_STATE(188)] = 3306,
  [SMALL_STATE(189)] = 3314,
  [SMALL_STATE(190)] = 3322,
  [SMALL_STATE(191)] = 3332,
  [SMALL_STATE(192)] = 3340,
  [SMALL_STATE(193)] = 3348,
  [SMALL_STATE(194)] = 3356,
  [SMALL_STATE(195)] = 3366,
  [SMALL_STATE(196)] = 3372,
  [SMALL_STATE(197)] = 3379,
  [SMALL_STATE(198)] = 3386,
  [SMALL_STATE(199)] = 3393,
  [SMALL_STATE(200)] = 3400,
  [SMALL_STATE(201)] = 3407,
  [SMALL_STATE(202)] = 3412,
  [SMALL_STATE(203)] = 3419,
  [SMALL_STATE(204)] = 3426,
  [SMALL_STATE(205)] = 3433,
  [SMALL_STATE(206)] = 3440,
  [SMALL_STATE(207)] = 3447,
  [SMALL_STATE(208)] = 3454,
  [SMALL_STATE(209)] = 3461,
  [SMALL_STATE(210)] = 3468,
  [SMALL_STATE(211)] = 3475,
  [SMALL_STATE(212)] = 3482,
  [SMALL_STATE(213)] = 3489,
  [SMALL_STATE(214)] = 3496,
  [SMALL_STATE(215)] = 3503,
  [SMALL_STATE(216)] = 3510,
  [SMALL_STATE(217)] = 3517,
  [SMALL_STATE(218)] = 3524,
  [SMALL_STATE(219)] = 3531,
  [SMALL_STATE(220)] = 3538,
  [SMALL_STATE(221)] = 3545,
  [SMALL_STATE(222)] = 3552,
  [SMALL_STATE(223)] = 3559,
  [SMALL_STATE(224)] = 3566,
  [SMALL_STATE(225)] = 3573,
  [SMALL_STATE(226)] = 3580,
  [SMALL_STATE(227)] = 3587,
  [SMALL_STATE(228)] = 3594,
  [SMALL_STATE(229)] = 3601,
  [SMALL_STATE(230)] = 3608,
  [SMALL_STATE(231)] = 3615,
  [SMALL_STATE(232)] = 3622,
  [SMALL_STATE(233)] = 3629,
  [SMALL_STATE(234)] = 3636,
  [SMALL_STATE(235)] = 3643,
  [SMALL_STATE(236)] = 3650,
  [SMALL_STATE(237)] = 3654,
  [SMALL_STATE(238)] = 3658,
  [SMALL_STATE(239)] = 3662,
  [SMALL_STATE(240)] = 3666,
  [SMALL_STATE(241)] = 3670,
  [SMALL_STATE(242)] = 3674,
  [SMALL_STATE(243)] = 3678,
  [SMALL_STATE(244)] = 3682,
  [SMALL_STATE(245)] = 3686,
  [SMALL_STATE(246)] = 3690,
  [SMALL_STATE(247)] = 3694,
  [SMALL_STATE(248)] = 3698,
  [SMALL_STATE(249)] = 3702,
  [SMALL_STATE(250)] = 3706,
  [SMALL_STATE(251)] = 3710,
  [SMALL_STATE(252)] = 3714,
  [SMALL_STATE(253)] = 3718,
  [SMALL_STATE(254)] = 3722,
  [SMALL_STATE(255)] = 3726,
  [SMALL_STATE(256)] = 3730,
  [SMALL_STATE(257)] = 3734,
  [SMALL_STATE(258)] = 3738,
  [SMALL_STATE(259)] = 3742,
  [SMALL_STATE(260)] = 3746,
  [SMALL_STATE(261)] = 3750,
  [SMALL_STATE(262)] = 3754,
  [SMALL_STATE(263)] = 3758,
  [SMALL_STATE(264)] = 3762,
  [SMALL_STATE(265)] = 3766,
  [SMALL_STATE(266)] = 3770,
  [SMALL_STATE(267)] = 3774,
  [SMALL_STATE(268)] = 3778,
  [SMALL_STATE(269)] = 3782,
  [SMALL_STATE(270)] = 3786,
  [SMALL_STATE(271)] = 3790,
  [SMALL_STATE(272)] = 3794,
  [SMALL_STATE(273)] = 3798,
  [SMALL_STATE(274)] = 3802,
  [SMALL_STATE(275)] = 3806,
  [SMALL_STATE(276)] = 3810,
  [SMALL_STATE(277)] = 3814,
  [SMALL_STATE(278)] = 3818,
  [SMALL_STATE(279)] = 3822,
  [SMALL_STATE(280)] = 3826,
  [SMALL_STATE(281)] = 3830,
  [SMALL_STATE(282)] = 3834,
  [SMALL_STATE(283)] = 3838,
  [SMALL_STATE(284)] = 3842,
  [SMALL_STATE(285)] = 3846,
  [SMALL_STATE(286)] = 3850,
  [SMALL_STATE(287)] = 3854,
  [SMALL_STATE(288)] = 3858,
  [SMALL_STATE(289)] = 3862,
  [SMALL_STATE(290)] = 3866,
  [SMALL_STATE(291)] = 3870,
  [SMALL_STATE(292)] = 3874,
  [SMALL_STATE(293)] = 3878,
  [SMALL_STATE(294)] = 3882,
  [SMALL_STATE(295)] = 3886,
  [SMALL_STATE(296)] = 3890,
  [SMALL_STATE(297)] = 3894,
  [SMALL_STATE(298)] = 3898,
  [SMALL_STATE(299)] = 3902,
};

static TSParseActionEntry ts_parse_actions[] = {
  [0] = {.count = 0, .reusable = false},
  [1] = {.count = 1, .reusable = false}, RECOVER(),
  [3] = {.count = 1, .reusable = true}, REDUCE(sym_beancount_file, 0),
  [5] = {.count = 1, .reusable = true}, SHIFT(265),
  [7] = {.count = 1, .reusable = true}, SHIFT(3),
  [9] = {.count = 1, .reusable = true}, SHIFT(293),
  [11] = {.count = 1, .reusable = true}, SHIFT(292),
  [13] = {.count = 1, .reusable = true}, SHIFT(291),
  [15] = {.count = 1, .reusable = true}, SHIFT(288),
  [17] = {.count = 1, .reusable = true}, SHIFT(287),
  [19] = {.count = 1, .reusable = true}, SHIFT(286),
  [21] = {.count = 1, .reusable = true}, SHIFT(213),
  [23] = {.count = 1, .reusable = true}, SHIFT(284),
  [25] = {.count = 1, .reusable = true}, SHIFT(16),
  [27] = {.count = 1, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2),
  [29] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(265),
  [32] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(2),
  [35] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(293),
  [38] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(292),
  [41] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(291),
  [44] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(288),
  [47] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(287),
  [50] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(286),
  [53] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(213),
  [56] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(284),
  [59] = {.count = 2, .reusable = true}, REDUCE(aux_sym_beancount_file_repeat1, 2), SHIFT_REPEAT(16),
  [62] = {.count = 1, .reusable = true}, REDUCE(sym_beancount_file, 1),
  [64] = {.count = 1, .reusable = true}, SHIFT(2),
  [66] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 2, .production_id = 10),
  [68] = {.count = 1, .reusable = true}, SHIFT(159),
  [70] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 2, .production_id = 10), SHIFT(235),
  [73] = {.count = 1, .reusable = false}, SHIFT(10),
  [75] = {.count = 1, .reusable = true}, SHIFT(11),
  [77] = {.count = 1, .reusable = true}, SHIFT(56),
  [79] = {.count = 1, .reusable = false}, SHIFT(56),
  [81] = {.count = 1, .reusable = true}, SHIFT(93),
  [83] = {.count = 1, .reusable = true}, SHIFT(99),
  [85] = {.count = 1, .reusable = true}, SHIFT(112),
  [87] = {.count = 1, .reusable = true}, SHIFT(78),
  [89] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 3, .production_id = 28),
  [91] = {.count = 1, .reusable = true}, SHIFT(163),
  [93] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 3, .production_id = 28), SHIFT(235),
  [96] = {.count = 1, .reusable = false}, SHIFT(38),
  [98] = {.count = 1, .reusable = true}, SHIFT(235),
  [100] = {.count = 1, .reusable = true}, SHIFT(97),
  [102] = {.count = 1, .reusable = true}, SHIFT(102),
  [104] = {.count = 1, .reusable = false}, SHIFT(12),
  [106] = {.count = 1, .reusable = true}, SHIFT(12),
  [108] = {.count = 1, .reusable = false}, SHIFT(26),
  [110] = {.count = 1, .reusable = false}, SHIFT(28),
  [112] = {.count = 1, .reusable = false}, SHIFT(6),
  [114] = {.count = 1, .reusable = true}, SHIFT(6),
  [116] = {.count = 1, .reusable = false}, REDUCE(sym_key_value, 1),
  [118] = {.count = 1, .reusable = true}, REDUCE(sym_key_value, 1),
  [120] = {.count = 1, .reusable = false}, SHIFT(232),
  [122] = {.count = 1, .reusable = true}, SHIFT(232),
  [124] = {.count = 1, .reusable = false}, SHIFT(111),
  [126] = {.count = 1, .reusable = true}, SHIFT(101),
  [128] = {.count = 1, .reusable = true}, SHIFT(91),
  [130] = {.count = 1, .reusable = false}, SHIFT(263),
  [132] = {.count = 1, .reusable = true}, SHIFT(263),
  [134] = {.count = 1, .reusable = false}, SHIFT(114),
  [136] = {.count = 1, .reusable = true}, SHIFT(122),
  [138] = {.count = 1, .reusable = true}, SHIFT(191),
  [140] = {.count = 1, .reusable = true}, SHIFT(87),
  [142] = {.count = 1, .reusable = true}, SHIFT(193),
  [144] = {.count = 1, .reusable = false}, SHIFT(88),
  [146] = {.count = 1, .reusable = false}, REDUCE(aux_sym_custom_repeat1, 2),
  [148] = {.count = 1, .reusable = true}, REDUCE(aux_sym_custom_repeat1, 2),
  [150] = {.count = 2, .reusable = true}, REDUCE(aux_sym_custom_repeat1, 2), SHIFT_REPEAT(97),
  [153] = {.count = 2, .reusable = true}, REDUCE(aux_sym_custom_repeat1, 2), SHIFT_REPEAT(102),
  [156] = {.count = 2, .reusable = false}, REDUCE(aux_sym_custom_repeat1, 2), SHIFT_REPEAT(12),
  [159] = {.count = 2, .reusable = true}, REDUCE(aux_sym_custom_repeat1, 2), SHIFT_REPEAT(12),
  [162] = {.count = 2, .reusable = false}, REDUCE(aux_sym_custom_repeat1, 2), SHIFT_REPEAT(26),
  [165] = {.count = 1, .reusable = true}, REDUCE(sym_poptag, 3, .production_id = 2),
  [167] = {.count = 1, .reusable = true}, REDUCE(sym_commodity, 5, .production_id = 14),
  [169] = {.count = 1, .reusable = true}, SHIFT(130),
  [171] = {.count = 1, .reusable = true}, SHIFT(245),
  [173] = {.count = 1, .reusable = true}, SHIFT(239),
  [175] = {.count = 1, .reusable = true}, SHIFT(249),
  [177] = {.count = 1, .reusable = true}, SHIFT(250),
  [179] = {.count = 1, .reusable = true}, SHIFT(251),
  [181] = {.count = 1, .reusable = true}, SHIFT(252),
  [183] = {.count = 1, .reusable = true}, SHIFT(253),
  [185] = {.count = 1, .reusable = true}, SHIFT(255),
  [187] = {.count = 1, .reusable = true}, SHIFT(256),
  [189] = {.count = 1, .reusable = true}, SHIFT(257),
  [191] = {.count = 1, .reusable = true}, SHIFT(258),
  [193] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 7, .production_id = 79),
  [195] = {.count = 1, .reusable = true}, REDUCE(sym__skipped_lines, 2),
  [197] = {.count = 1, .reusable = true}, REDUCE(sym_close, 5, .production_id = 13),
  [199] = {.count = 1, .reusable = false}, REDUCE(sym_binary_num_expr, 3),
  [201] = {.count = 1, .reusable = true}, REDUCE(sym_binary_num_expr, 3),
  [203] = {.count = 1, .reusable = true}, SHIFT(106),
  [205] = {.count = 1, .reusable = true}, REDUCE(sym_open, 7, .production_id = 61),
  [207] = {.count = 1, .reusable = true}, REDUCE(sym_document, 7, .production_id = 60),
  [209] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 6, .production_id = 59),
  [211] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 6, .production_id = 58),
  [213] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 6, .production_id = 57),
  [215] = {.count = 1, .reusable = false}, REDUCE(aux_sym_custom_repeat1, 1),
  [217] = {.count = 1, .reusable = true}, REDUCE(aux_sym_custom_repeat1, 1),
  [219] = {.count = 1, .reusable = true}, SHIFT(108),
  [221] = {.count = 1, .reusable = false}, SHIFT(85),
  [223] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 4, .production_id = 11),
  [225] = {.count = 1, .reusable = true}, REDUCE(sym_custom, 4, .production_id = 9),
  [227] = {.count = 1, .reusable = true}, REDUCE(sym_query, 6, .production_id = 43),
  [229] = {.count = 1, .reusable = true}, REDUCE(sym_price, 6, .production_id = 42),
  [231] = {.count = 1, .reusable = true}, REDUCE(sym_pad, 6, .production_id = 41),
  [233] = {.count = 1, .reusable = true}, REDUCE(sym_open, 6, .production_id = 40),
  [235] = {.count = 1, .reusable = true}, REDUCE(sym_open, 6, .production_id = 39),
  [237] = {.count = 1, .reusable = true}, REDUCE(sym_open, 6, .production_id = 38),
  [239] = {.count = 1, .reusable = true}, REDUCE(sym_note, 6, .production_id = 37),
  [241] = {.count = 1, .reusable = true}, REDUCE(sym_event, 6, .production_id = 36),
  [243] = {.count = 1, .reusable = true}, REDUCE(sym_document, 6, .production_id = 35),
  [245] = {.count = 1, .reusable = true}, REDUCE(sym_custom, 5, .production_id = 9),
  [247] = {.count = 1, .reusable = true}, REDUCE(sym__skipped_lines, 3),
  [249] = {.count = 1, .reusable = true}, REDUCE(sym_include, 3),
  [251] = {.count = 1, .reusable = true}, REDUCE(sym_document, 6, .production_id = 34),
  [253] = {.count = 1, .reusable = true}, REDUCE(sym_plugin, 3, .production_id = 1),
  [255] = {.count = 1, .reusable = true}, REDUCE(sym_custom, 6, .production_id = 33),
  [257] = {.count = 1, .reusable = true}, REDUCE(sym_pushtag, 3, .production_id = 2),
  [259] = {.count = 1, .reusable = true}, REDUCE(sym_balance, 6, .production_id = 32),
  [261] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 5, .production_id = 31),
  [263] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 5, .production_id = 30),
  [265] = {.count = 1, .reusable = true}, REDUCE(sym_transaction, 5, .production_id = 29),
  [267] = {.count = 1, .reusable = true}, REDUCE(sym_pushmeta, 3, .production_id = 3),
  [269] = {.count = 1, .reusable = true}, REDUCE(sym_popmeta, 3, .production_id = 4),
  [271] = {.count = 1, .reusable = true}, REDUCE(sym_commodity, 4, .production_id = 8),
  [273] = {.count = 1, .reusable = true}, REDUCE(sym_custom, 5, .production_id = 15),
  [275] = {.count = 1, .reusable = true}, REDUCE(sym_balance, 5, .production_id = 12),
  [277] = {.count = 1, .reusable = true}, REDUCE(sym_close, 4, .production_id = 7),
  [279] = {.count = 1, .reusable = false}, REDUCE(sym_price_annotation, 1),
  [281] = {.count = 1, .reusable = true}, REDUCE(sym_price_annotation, 1),
  [283] = {.count = 1, .reusable = true}, REDUCE(sym_open, 4, .production_id = 7),
  [285] = {.count = 1, .reusable = false}, REDUCE(sym__paren_num_expr, 3),
  [287] = {.count = 1, .reusable = true}, REDUCE(sym__paren_num_expr, 3),
  [289] = {.count = 1, .reusable = true}, REDUCE(sym_query, 5, .production_id = 23),
  [291] = {.count = 1, .reusable = true}, REDUCE(sym_plugin, 4, .production_id = 6),
  [293] = {.count = 1, .reusable = true}, REDUCE(sym_price, 5, .production_id = 22),
  [295] = {.count = 1, .reusable = true}, REDUCE(sym_pad, 5, .production_id = 21),
  [297] = {.count = 1, .reusable = true}, REDUCE(sym_open, 5, .production_id = 20),
  [299] = {.count = 1, .reusable = true}, REDUCE(sym_open, 5, .production_id = 13),
  [301] = {.count = 1, .reusable = true}, REDUCE(sym_open, 5, .production_id = 19),
  [303] = {.count = 1, .reusable = true}, REDUCE(sym_note, 5, .production_id = 18),
  [305] = {.count = 1, .reusable = true}, REDUCE(sym_option, 4, .production_id = 5),
  [307] = {.count = 1, .reusable = true}, REDUCE(sym_event, 5, .production_id = 17),
  [309] = {.count = 1, .reusable = true}, REDUCE(sym_document, 5, .production_id = 16),
  [311] = {.count = 1, .reusable = false}, REDUCE(sym_unary_num_expr, 2),
  [313] = {.count = 1, .reusable = true}, REDUCE(sym_unary_num_expr, 2),
  [315] = {.count = 1, .reusable = true}, SHIFT(98),
  [317] = {.count = 1, .reusable = true}, SHIFT(90),
  [319] = {.count = 1, .reusable = false}, REDUCE(sym_incomplete_amount, 1),
  [321] = {.count = 1, .reusable = true}, REDUCE(sym_incomplete_amount, 1),
  [323] = {.count = 1, .reusable = true}, SHIFT(95),
  [325] = {.count = 1, .reusable = true}, SHIFT(109),
  [327] = {.count = 1, .reusable = true}, SHIFT(104),
  [329] = {.count = 1, .reusable = true}, SHIFT(132),
  [331] = {.count = 1, .reusable = true}, SHIFT(154),
  [333] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 3, .production_id = 26),
  [335] = {.count = 1, .reusable = true}, SHIFT(171),
  [337] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 3, .production_id = 26), SHIFT(235),
  [340] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 55),
  [342] = {.count = 1, .reusable = true}, SHIFT(144),
  [344] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 55), SHIFT(235),
  [347] = {.count = 1, .reusable = true}, SHIFT(117),
  [349] = {.count = 1, .reusable = false}, REDUCE(sym_amount, 2),
  [351] = {.count = 1, .reusable = true}, REDUCE(sym_amount, 2),
  [353] = {.count = 1, .reusable = true}, SHIFT(128),
  [355] = {.count = 1, .reusable = true}, SHIFT(192),
  [357] = {.count = 1, .reusable = true}, SHIFT(137),
  [359] = {.count = 1, .reusable = false}, REDUCE(sym_compound_amount, 1, .production_id = 46),
  [361] = {.count = 1, .reusable = true}, REDUCE(sym_compound_amount, 1, .production_id = 46),
  [363] = {.count = 1, .reusable = true}, SHIFT(89),
  [365] = {.count = 1, .reusable = true}, SHIFT(92),
  [367] = {.count = 1, .reusable = true}, SHIFT(186),
  [369] = {.count = 1, .reusable = true}, SHIFT(187),
  [371] = {.count = 1, .reusable = true}, SHIFT(119),
  [373] = {.count = 1, .reusable = true}, SHIFT(75),
  [375] = {.count = 1, .reusable = true}, SHIFT(72),
  [377] = {.count = 1, .reusable = true}, SHIFT(76),
  [379] = {.count = 1, .reusable = true}, SHIFT(141),
  [381] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 76),
  [383] = {.count = 1, .reusable = true}, SHIFT(168),
  [385] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 76), SHIFT(235),
  [388] = {.count = 1, .reusable = true}, SHIFT(73),
  [390] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 3, .production_id = 25),
  [392] = {.count = 1, .reusable = true}, SHIFT(174),
  [394] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 3, .production_id = 25), SHIFT(235),
  [397] = {.count = 1, .reusable = true}, SHIFT(134),
  [399] = {.count = 1, .reusable = true}, SHIFT(74),
  [401] = {.count = 1, .reusable = true}, SHIFT(79),
  [403] = {.count = 1, .reusable = false}, SHIFT(69),
  [405] = {.count = 1, .reusable = true}, SHIFT(182),
  [407] = {.count = 1, .reusable = true}, SHIFT(123),
  [409] = {.count = 1, .reusable = true}, SHIFT(70),
  [411] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 50),
  [413] = {.count = 1, .reusable = true}, SHIFT(153),
  [415] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 50), SHIFT(235),
  [418] = {.count = 1, .reusable = false}, SHIFT(130),
  [420] = {.count = 1, .reusable = true}, SHIFT(209),
  [422] = {.count = 1, .reusable = true}, SHIFT(8),
  [424] = {.count = 1, .reusable = true}, SHIFT(167),
  [426] = {.count = 1, .reusable = true}, SHIFT(4),
  [428] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 54),
  [430] = {.count = 1, .reusable = true}, SHIFT(148),
  [432] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 54), SHIFT(235),
  [435] = {.count = 1, .reusable = true}, SHIFT(55),
  [437] = {.count = 1, .reusable = true}, SHIFT(124),
  [439] = {.count = 1, .reusable = true}, SHIFT(20),
  [441] = {.count = 1, .reusable = false}, REDUCE(sym_incomplete_amount, 2),
  [443] = {.count = 1, .reusable = true}, REDUCE(sym_incomplete_amount, 2),
  [445] = {.count = 1, .reusable = false}, SHIFT(57),
  [447] = {.count = 1, .reusable = true}, SHIFT(158),
  [449] = {.count = 1, .reusable = true}, SHIFT(135),
  [451] = {.count = 1, .reusable = false}, REDUCE(sym__key_value_value, 1),
  [453] = {.count = 1, .reusable = true}, REDUCE(sym__key_value_value, 1),
  [455] = {.count = 1, .reusable = true}, SHIFT(85),
  [457] = {.count = 1, .reusable = true}, SHIFT(246),
  [459] = {.count = 1, .reusable = true}, SHIFT(113),
  [461] = {.count = 1, .reusable = true}, SHIFT(107),
  [463] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 48),
  [465] = {.count = 1, .reusable = true}, SHIFT(156),
  [467] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 48), SHIFT(235),
  [470] = {.count = 1, .reusable = true}, SHIFT(189),
  [472] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 74),
  [474] = {.count = 1, .reusable = true}, SHIFT(175),
  [476] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 74), SHIFT(235),
  [479] = {.count = 1, .reusable = false}, REDUCE(aux_sym_currency_list_repeat1, 2),
  [481] = {.count = 1, .reusable = true}, REDUCE(aux_sym_currency_list_repeat1, 2),
  [483] = {.count = 2, .reusable = true}, REDUCE(aux_sym_currency_list_repeat1, 2), SHIFT_REPEAT(236),
  [486] = {.count = 1, .reusable = false}, REDUCE(sym_cost_spec, 2),
  [488] = {.count = 1, .reusable = true}, REDUCE(sym_cost_spec, 2),
  [490] = {.count = 1, .reusable = true}, SHIFT(71),
  [492] = {.count = 1, .reusable = true}, SHIFT(212),
  [494] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 51),
  [496] = {.count = 1, .reusable = true}, SHIFT(149),
  [498] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 51), SHIFT(235),
  [501] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 90),
  [503] = {.count = 1, .reusable = true}, SHIFT(155),
  [505] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 90), SHIFT(235),
  [508] = {.count = 1, .reusable = false}, REDUCE(aux_sym_tags_and_links_repeat1, 2),
  [510] = {.count = 2, .reusable = true}, REDUCE(aux_sym_tags_and_links_repeat1, 2), SHIFT_REPEAT(201),
  [513] = {.count = 2, .reusable = true}, REDUCE(aux_sym_tags_and_links_repeat1, 2), SHIFT_REPEAT(127),
  [516] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 56),
  [518] = {.count = 1, .reusable = true}, SHIFT(177),
  [520] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 56), SHIFT(235),
  [523] = {.count = 1, .reusable = true}, REDUCE(sym_flag, 1),
  [525] = {.count = 1, .reusable = false}, SHIFT(63),
  [527] = {.count = 1, .reusable = true}, SHIFT(152),
  [529] = {.count = 1, .reusable = false}, REDUCE(sym_tags_and_links, 1),
  [531] = {.count = 2, .reusable = true}, REDUCE(sym_tags_and_links, 1), SHIFT(201),
  [534] = {.count = 1, .reusable = true}, SHIFT(127),
  [536] = {.count = 1, .reusable = false}, REDUCE(sym_currency_list, 2),
  [538] = {.count = 1, .reusable = true}, REDUCE(sym_currency_list, 2),
  [540] = {.count = 1, .reusable = true}, SHIFT(236),
  [542] = {.count = 1, .reusable = true}, SHIFT(58),
  [544] = {.count = 1, .reusable = false}, REDUCE(sym_currency_list, 1),
  [546] = {.count = 1, .reusable = true}, REDUCE(sym_currency_list, 1),
  [548] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 77),
  [550] = {.count = 1, .reusable = true}, SHIFT(142),
  [552] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 77), SHIFT(235),
  [555] = {.count = 1, .reusable = true}, SHIFT(183),
  [557] = {.count = 1, .reusable = false}, REDUCE(sym_cost_spec, 3, .production_id = 63),
  [559] = {.count = 1, .reusable = true}, REDUCE(sym_cost_spec, 3, .production_id = 63),
  [561] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 3, .production_id = 27),
  [563] = {.count = 1, .reusable = true}, SHIFT(169),
  [565] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 3, .production_id = 27), SHIFT(235),
  [568] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 69),
  [570] = {.count = 1, .reusable = true}, SHIFT(179),
  [572] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 69), SHIFT(235),
  [575] = {.count = 1, .reusable = true}, SHIFT(77),
  [577] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 77),
  [579] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 77), SHIFT(235),
  [582] = {.count = 1, .reusable = false}, REDUCE(aux_sym_cost_comp_list_repeat1, 2),
  [584] = {.count = 1, .reusable = true}, REDUCE(aux_sym_cost_comp_list_repeat1, 2),
  [586] = {.count = 2, .reusable = true}, REDUCE(aux_sym_cost_comp_list_repeat1, 2), SHIFT_REPEAT(13),
  [589] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 55),
  [591] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 55), SHIFT(235),
  [594] = {.count = 1, .reusable = false}, SHIFT(37),
  [596] = {.count = 1, .reusable = false}, REDUCE(sym_postings, 1),
  [598] = {.count = 1, .reusable = true}, SHIFT(172),
  [600] = {.count = 1, .reusable = false}, SHIFT(68),
  [602] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 54),
  [604] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 54), SHIFT(235),
  [607] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 51),
  [609] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 51), SHIFT(235),
  [612] = {.count = 1, .reusable = false}, SHIFT(66),
  [614] = {.count = 1, .reusable = false}, SHIFT(33),
  [616] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 50),
  [618] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 50), SHIFT(235),
  [621] = {.count = 1, .reusable = true}, REDUCE(sym_txn_strings, 1),
  [623] = {.count = 1, .reusable = true}, SHIFT(195),
  [625] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 7, .production_id = 90),
  [627] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 7, .production_id = 90), SHIFT(235),
  [630] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 48),
  [632] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 48), SHIFT(235),
  [635] = {.count = 1, .reusable = false}, REDUCE(sym_cost_comp_list, 2),
  [637] = {.count = 1, .reusable = true}, REDUCE(sym_cost_comp_list, 2),
  [639] = {.count = 1, .reusable = true}, SHIFT(13),
  [641] = {.count = 1, .reusable = false}, SHIFT(65),
  [643] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 3, .production_id = 10),
  [645] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 3, .production_id = 10), SHIFT(235),
  [648] = {.count = 1, .reusable = false}, SHIFT(62),
  [650] = {.count = 1, .reusable = false}, SHIFT(61),
  [652] = {.count = 1, .reusable = false}, SHIFT(59),
  [654] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 28),
  [656] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 28), SHIFT(235),
  [659] = {.count = 1, .reusable = false}, SHIFT(51),
  [661] = {.count = 1, .reusable = false}, SHIFT(54),
  [663] = {.count = 1, .reusable = false}, SHIFT(53),
  [665] = {.count = 1, .reusable = true}, REDUCE(aux_sym_tags_and_links_repeat1, 2),
  [667] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 76),
  [669] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 76), SHIFT(235),
  [672] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 27),
  [674] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 27), SHIFT(235),
  [677] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 26),
  [679] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 26), SHIFT(235),
  [682] = {.count = 1, .reusable = false}, REDUCE(aux_sym_postings_repeat1, 2),
  [684] = {.count = 2, .reusable = true}, REDUCE(aux_sym_postings_repeat1, 2), SHIFT_REPEAT(172),
  [687] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 25),
  [689] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 25), SHIFT(235),
  [692] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 74),
  [694] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 74), SHIFT(235),
  [697] = {.count = 1, .reusable = false}, REDUCE(sym_cost_comp_list, 1),
  [699] = {.count = 1, .reusable = true}, REDUCE(sym_cost_comp_list, 1),
  [701] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 56),
  [703] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 56), SHIFT(235),
  [706] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 69),
  [708] = {.count = 2, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 69), SHIFT(235),
  [711] = {.count = 1, .reusable = false}, REDUCE(sym_compound_amount, 3, .production_id = 80),
  [713] = {.count = 1, .reusable = true}, REDUCE(sym_compound_amount, 3, .production_id = 80),
  [715] = {.count = 1, .reusable = false}, REDUCE(sym_price_annotation, 2),
  [717] = {.count = 1, .reusable = true}, REDUCE(sym_price_annotation, 2),
  [719] = {.count = 1, .reusable = false}, REDUCE(sym_metadata, 1),
  [721] = {.count = 2, .reusable = true}, REDUCE(sym_metadata, 1), SHIFT(235),
  [724] = {.count = 1, .reusable = false}, REDUCE(sym_compound_amount, 2, .production_id = 64),
  [726] = {.count = 1, .reusable = true}, REDUCE(sym_compound_amount, 2, .production_id = 64),
  [728] = {.count = 1, .reusable = false}, REDUCE(sym_compound_amount, 3, .production_id = 81),
  [730] = {.count = 1, .reusable = true}, REDUCE(sym_compound_amount, 3, .production_id = 81),
  [732] = {.count = 1, .reusable = false}, REDUCE(sym_compound_amount, 4, .production_id = 93),
  [734] = {.count = 1, .reusable = true}, REDUCE(sym_compound_amount, 4, .production_id = 93),
  [736] = {.count = 1, .reusable = false}, REDUCE(sym_cost_comp, 1),
  [738] = {.count = 1, .reusable = true}, REDUCE(sym_cost_comp, 1),
  [740] = {.count = 1, .reusable = false}, REDUCE(sym_compound_amount, 2, .production_id = 62),
  [742] = {.count = 1, .reusable = true}, REDUCE(sym_compound_amount, 2, .production_id = 62),
  [744] = {.count = 1, .reusable = false}, REDUCE(sym_compound_amount, 1, .production_id = 45),
  [746] = {.count = 1, .reusable = true}, REDUCE(sym_compound_amount, 1, .production_id = 45),
  [748] = {.count = 1, .reusable = false}, REDUCE(aux_sym_metadata_repeat1, 2),
  [750] = {.count = 2, .reusable = true}, REDUCE(aux_sym_metadata_repeat1, 2), SHIFT_REPEAT(235),
  [753] = {.count = 1, .reusable = true}, REDUCE(sym_txn_strings, 2),
  [755] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 91),
  [757] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 91),
  [759] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 78),
  [761] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 78),
  [763] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 85),
  [765] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 85),
  [767] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 86),
  [769] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 86),
  [771] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 47),
  [773] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 47),
  [775] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 49),
  [777] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 49),
  [779] = {.count = 1, .reusable = true}, REDUCE(aux_sym_metadata_repeat1, 2),
  [781] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 87),
  [783] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 87),
  [785] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 52),
  [787] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 52),
  [789] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 88),
  [791] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 88),
  [793] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 89),
  [795] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 89),
  [797] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 53),
  [799] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 53),
  [801] = {.count = 1, .reusable = true}, REDUCE(aux_sym_postings_repeat1, 2),
  [803] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 83),
  [805] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 83),
  [807] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 3, .production_id = 24),
  [809] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 3, .production_id = 24),
  [811] = {.count = 1, .reusable = false}, REDUCE(sym_amount_with_tolerance, 4),
  [813] = {.count = 1, .reusable = true}, REDUCE(sym_amount_with_tolerance, 4),
  [815] = {.count = 1, .reusable = true}, SHIFT(9),
  [817] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 92),
  [819] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 92),
  [821] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 84),
  [823] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 84),
  [825] = {.count = 1, .reusable = true}, SHIFT(42),
  [827] = {.count = 1, .reusable = true}, SHIFT(261),
  [829] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 7, .production_id = 94),
  [831] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 7, .production_id = 94),
  [833] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 4, .production_id = 44),
  [835] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 4, .production_id = 44),
  [837] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 65),
  [839] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 65),
  [841] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 7, .production_id = 95),
  [843] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 7, .production_id = 95),
  [845] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 66),
  [847] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 66),
  [849] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 67),
  [851] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 67),
  [853] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 7, .production_id = 96),
  [855] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 7, .production_id = 96),
  [857] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 68),
  [859] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 68),
  [861] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 7, .production_id = 97),
  [863] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 7, .production_id = 97),
  [865] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 7, .production_id = 98),
  [867] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 7, .production_id = 98),
  [869] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 70),
  [871] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 70),
  [873] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 71),
  [875] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 71),
  [877] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 72),
  [879] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 72),
  [881] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 8, .production_id = 99),
  [883] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 8, .production_id = 99),
  [885] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 73),
  [887] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 73),
  [889] = {.count = 1, .reusable = false}, REDUCE(sym_key_value, 2),
  [891] = {.count = 1, .reusable = true}, REDUCE(sym_key_value, 2),
  [893] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 6, .production_id = 82),
  [895] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 6, .production_id = 82),
  [897] = {.count = 1, .reusable = false}, REDUCE(sym_posting, 5, .production_id = 75),
  [899] = {.count = 1, .reusable = true}, REDUCE(sym_posting, 5, .production_id = 75),
  [901] = {.count = 1, .reusable = true}, SHIFT(181),
  [903] = {.count = 1, .reusable = true}, SHIFT(14),
  [905] = {.count = 1, .reusable = true}, SHIFT(44),
  [907] = {.count = 1, .reusable = true}, SHIFT(165),
  [909] = {.count = 1, .reusable = true}, SHIFT(138),
  [911] = {.count = 1, .reusable = true}, SHIFT(50),
  [913] = {.count = 1, .reusable = true}, SHIFT(17),
  [915] = {.count = 1, .reusable = true}, SHIFT(49),
  [917] = {.count = 1, .reusable = true}, SHIFT(260),
  [919] = {.count = 1, .reusable = true}, SHIFT(84),
  [921] = {.count = 1, .reusable = true}, SHIFT(40),
  [923] = {.count = 1, .reusable = true}, SHIFT(164),
  [925] = {.count = 1, .reusable = true}, SHIFT(7),
  [927] = {.count = 1, .reusable = true}, SHIFT(267),
  [929] = {.count = 1, .reusable = true}, SHIFT(268),
  [931] = {.count = 1, .reusable = true}, SHIFT(269),
  [933] = {.count = 1, .reusable = true}, SHIFT(21),
  [935] = {.count = 1, .reusable = true}, SHIFT(110),
  [937] = {.count = 1, .reusable = true}, SHIFT(270),
  [939] = {.count = 1, .reusable = true}, SHIFT(86),
  [941] = {.count = 1, .reusable = true}, SHIFT(272),
  [943] = {.count = 1, .reusable = true}, SHIFT(22),
  [945] = {.count = 1, .reusable = true}, SHIFT(67),
  [947] = {.count = 1, .reusable = true}, SHIFT(60),
  [949] = {.count = 1, .reusable = true}, SHIFT(23),
  [951] = {.count = 1, .reusable = true}, SHIFT(24),
  [953] = {.count = 1, .reusable = true}, SHIFT(277),
  [955] = {.count = 1, .reusable = true}, SHIFT(25),
  [957] = {.count = 1, .reusable = true}, SHIFT(100),
  [959] = {.count = 1, .reusable = true}, SHIFT(147),
  [961] = {.count = 1, .reusable = true}, SHIFT(150),
  [963] = {.count = 1, .reusable = true}, SHIFT(160),
  [965] = {.count = 1, .reusable = true}, SHIFT(29),
  [967] = {.count = 1, .reusable = true}, SHIFT(162),
  [969] = {.count = 1, .reusable = true}, SHIFT(30),
  [971] = {.count = 1, .reusable = true}, SHIFT(31),
  [973] = {.count = 1, .reusable = true}, SHIFT(32),
  [975] = {.count = 1, .reusable = true}, SHIFT(27),
  [977] = {.count = 1, .reusable = true}, SHIFT(39),
  [979] = {.count = 1, .reusable = true}, SHIFT(34),
  [981] = {.count = 1, .reusable = true}, SHIFT(35),
  [983] = {.count = 1, .reusable = true}, SHIFT(36),
  [985] = {.count = 1, .reusable = true},  ACCEPT_INPUT(),
  [987] = {.count = 1, .reusable = true}, SHIFT(41),
  [989] = {.count = 1, .reusable = true}, SHIFT(43),
  [991] = {.count = 1, .reusable = true}, SHIFT(241),
  [993] = {.count = 1, .reusable = true}, SHIFT(45),
  [995] = {.count = 1, .reusable = true}, SHIFT(237),
  [997] = {.count = 1, .reusable = true}, SHIFT(238),
  [999] = {.count = 1, .reusable = true}, SHIFT(216),
  [1001] = {.count = 1, .reusable = true}, SHIFT(46),
  [1003] = {.count = 1, .reusable = true}, SHIFT(47),
  [1005] = {.count = 1, .reusable = true}, SHIFT(244),
  [1007] = {.count = 1, .reusable = true}, SHIFT(248),
  [1009] = {.count = 1, .reusable = true}, SHIFT(18),
  [1011] = {.count = 1, .reusable = true}, SHIFT(48),
  [1013] = {.count = 1, .reusable = true}, SHIFT(5),
  [1015] = {.count = 1, .reusable = true}, SHIFT(64),
  [1017] = {.count = 1, .reusable = true}, SHIFT(52),
  [1019] = {.count = 1, .reusable = true}, SHIFT(15),
  [1021] = {.count = 1, .reusable = true}, SHIFT(19),
};

#ifdef __cplusplus
extern "C" {
#endif
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
#ifdef __cplusplus
}
#endif
