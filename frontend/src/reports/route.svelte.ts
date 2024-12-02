/** Create a reactive props proxy to allow updating of props. */
export function updateable_props<T extends Record<string, unknown>>(
  raw_props: T,
): [props: T, update: (v: T) => void] {
  // TODO: this makes it deeply reactive, which adds unnecessary overhead
  const props = $state(raw_props);
  return [
    props,
    (new_props) => {
      Object.assign(props, new_props);
    },
  ];
}
