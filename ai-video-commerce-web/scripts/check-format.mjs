import {
  readdir,
  readFile,
} from 'node:fs/promises'
import {
  relative,
  resolve,
} from 'node:path'
import {
  fileURLToPath,
} from 'node:url'

const projectRoot = resolve(
  fileURLToPath(new URL('..', import.meta.url)),
)
const roots = [
  resolve(projectRoot, 'src'),
  resolve(projectRoot, 'scripts'),
]
const supportedExtensions = /\.(?:css|js|mjs|vue)$/
const problems = []

async function collectFiles(directory) {
  const entries = await readdir(directory, {
    withFileTypes: true,
  })
  const files = []

  for (const entry of entries) {
    const path = resolve(directory, entry.name)

    if (entry.isDirectory()) {
      files.push(...await collectFiles(path))
    } else if (supportedExtensions.test(entry.name)) {
      files.push(path)
    }
  }

  return files
}

for (const root of roots) {
  for (const file of await collectFiles(root)) {
    const content = await readFile(file, 'utf8')
    const lines = content.split(/\r?\n/)

    lines.forEach((line, index) => {
      if (/[ \t]+$/.test(line)) {
        problems.push(
          `${relative(projectRoot, file)}:${index + 1} trailing whitespace`,
        )
      }
    })
  }
}

if (problems.length > 0) {
  problems.forEach((problem) => console.error(problem))
  process.exitCode = 1
} else {
  console.log('Format check passed (no trailing whitespace).')
}
