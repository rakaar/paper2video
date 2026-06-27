import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import Ajv from 'ajv';

const schemaPath = path.resolve('schemas/storyboard.schema.json');
const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
const ajv = new Ajv({allErrors: true});
const validate = ajv.compile(schema);

const storyboardPaths =
  process.argv.length > 2
    ? process.argv.slice(2)
    : ['src/storyboard.json', 'src/storyboard.voiceover.json'];

let failed = false;

for (const storyboardPath of storyboardPaths) {
  const absolutePath = path.resolve(storyboardPath);
  const storyboard = JSON.parse(fs.readFileSync(absolutePath, 'utf8'));
  const ok = validate(storyboard);

  if (!ok) {
    failed = true;
    console.error(`invalid storyboard: ${storyboardPath}`);
    for (const error of validate.errors ?? []) {
      console.error(`  ${error.instancePath || '/'} ${error.message}`);
    }
    continue;
  }

  console.log(`valid storyboard: ${storyboardPath}`);
}

if (failed) {
  process.exit(1);
}
