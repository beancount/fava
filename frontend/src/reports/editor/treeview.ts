export interface FileNode {
  name: string;
  path: string;
  action: () => void;
}
export interface FolderNode {
  name: string;
  subfolders: FolderNode[];
  subfiles: FileNode[];
}

const zip: <A, B>(a: A[], b: B[]) => [A, B][] = <A, B>(a: A[], b: B[]) =>
  a.reduce((l: [A, B][], k: A, i) => {
    const n = b[i];
    if (n !== undefined) {
      l.push([k, n]);
    }
    return l;
  }, []);

function shorten_folder(folder: FolderNode): FolderNode {
  if (folder.subfiles.length === 0) {
    const subfolder = folder.subfolders[0];
    if (subfolder !== undefined) {
      const new_name = `${folder.name}/${subfolder.name}`;
      return shorten_folder({
        name: new_name,
        subfolders: subfolder.subfolders,
        subfiles: subfolder.subfiles,
      });
    }
  }
  return {
    name: folder.name,
    subfolders: folder.subfolders.map(shorten_folder),
    subfiles: folder.subfiles,
  };
}
function _source_tree(
  paths: string[][],
  filenodes: FileNode[]
): [FileNode[], FolderNode[]] {
  const groupBy = <T>(arr: T[], key: (i: T) => string) =>
    arr.reduce<Record<string, T[]>>((groups, item) => {
      (groups[key(item)] ||= []).push(item);
      return groups;
    }, {});

  const r1 = zip(filenodes, paths)
    .filter((a) => a[1].length === 0)
    .map((a) => a[0]);
  const r2 = Object.entries(
    groupBy(
      zip(filenodes, paths).reduce(
        (acc: [FileNode, string[], string][], [file, path]) => {
          const root = path[0];
          if (root !== undefined) {
            acc.push([file, path.slice(1), root]);
          }
          return acc;
        },
        []
      ),
      (a: [FileNode, string[], string]) => a[2]
    )
  ).map(([dir, group]: [string, [FileNode, string[], string][]]) => {
    const [subfiles, subfolders] = _source_tree(
      group.map((a: [FileNode, string[], string]) => a[1]),
      group.map((a: [FileNode, string[], string]) => a[0])
    );
    return { name: dir, subfolders, subfiles };
  });
  return [r1, r2];
}
export function source_tree(
  files: string[],
  goToFileAndLine: (filename: string, line?: number) => void
): [FileNode[], FolderNode[]] {
  files.sort();
  const paths = files.map((file) => file.split("/"));
  const raw_filenodes = zip(files, paths).map(
    ([file, path]: [string, string[]]) => ({
      name: path.pop() ?? file,
      path: file,
      action: () => goToFileAndLine(file),
    })
  );
  const [filenodes, foldernodes] = _source_tree(paths, raw_filenodes);
  return [filenodes, foldernodes.map(shorten_folder)];
}
