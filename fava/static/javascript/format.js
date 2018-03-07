// Helper functions to format numbers and dates.

import { format } from 'd3-format';
import { utcFormat } from 'd3-time-format';

const formatCurrencyWithComma = format(',.2f');
const formatCurrencyWithoutComma = format('.2f');
export function formatCurrency(number) {
  let str = '';
  if (window.favaAPI.options.render_commas) {
    str = formatCurrencyWithComma(number);
  } else {
    str = formatCurrencyWithoutComma(number);
  }
  if (window.favaAPI.incognito) {
    str = str.replace(/[0-9]/g, 'X');
  }
  return str;
}

const formatCurrencyShortDefault = format('.2s');
export function formatCurrencyShort(number) {
  let str = formatCurrencyShortDefault(number);
  if (window.favaAPI.incognito) {
    str = str.replace(/[0-9]/g, 'X');
  }
  return str;
}

export const dateFormat = {
  year: utcFormat('%Y'),
  quarter(date) {
    return `${date.getUTCFullYear()}Q${Math.floor(date.getUTCMonth() / 3) + 1}`;
  },
  month: utcFormat('%b %Y'),
  week: utcFormat('%YW%W'),
  day: utcFormat('%Y-%m-%d'),
};

export const timeFilterDateFormat = {
  year: utcFormat('%Y'),
  quarter(date) {
    return `${date.getUTCFullYear()}Q${Math.floor(date.getUTCMonth() / 3) + 1}`;
  },
  month: utcFormat('%Y-%m'),
  week: utcFormat('%Y-W%W'),
  day: utcFormat('%Y-%m-%d'),
};
