/** Libro de revisión: insumos JSON preparados por el análisis Python.
 * Requiere @oai/artifact-tool del runtime de documentos de Codex.
 * Uso: node crear_excel_revision.mjs entrada.json salida.xlsx directorio_qa
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const [input, output, qaDir, renderOnly] = process.argv.slice(2);
if (!input || !output || !qaDir) throw new Error('Se requieren entrada.json salida.xlsx directorio_qa');
const spec = JSON.parse(await fs.readFile(input, 'utf8'));
const wb = Workbook.create();
await fs.mkdir(path.dirname(output), { recursive: true });
await fs.mkdir(qaDir, { recursive: true });
const letter = n => { let s=''; for(n++;n>0;n=Math.floor((n-1)/26)) s=String.fromCharCode(65+(n-1)%26)+s; return s; };
const diagnostics = [];
for (const def of spec.sheets) {
  const s = wb.worksheets.add(def.name);
  s.showGridLines = false;
  const n=def.columns.length, last=letter(n-1), end=5+def.rows.length;
  if(end>1048576) throw new Error(`Límite Excel: ${def.name}`);
  s.getRange(`A1:${last}${end}`).format.font={name:'Arial',size:10,color:'#24354B'};
  s.getRange(`A1:${last}${end}`).format.verticalAlignment='center';
  s.getRange('A2').values=[[def.title]];
  s.getRange('A2').format.font={name:'Arial',size:15,bold:true,color:'#183453'};
  s.getRange('A3').values=[[def.note || '']];
  s.getRange('A3').format.font={name:'Arial',size:10,italic:true,color:'#536276'};
  s.getRange(`A5:${last}5`).values=[def.columns.map(c=>c.label)];
  s.getRange(`A5:${last}5`).format={fill:'#244666',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:42,horizontalAlignment:'center',verticalAlignment:'center'};
  const rows=def.rows.map(row=>def.columns.map(c=>{
    const value=row[c.key];
    if(value===null||value===undefined) return null;
    if(c.type==='date') return new Date(value+'T12:00:00Z');
    if(typeof value==='string' && value.startsWith('=')) return "'"+value;
    return value;
  }));
  if(rows.length) {
    s.getRange(`A6:${last}${end}`).values=rows;
    s.getRange(`A6:${last}${end}`).format.rowHeight=def.rowHeight || 23;
  }
  for(let i=0;i<n;i++) {
    const c=def.columns[i], col=letter(i);
    s.getRange(`${col}1:${col}${end}`).format.columnWidth=c.width || 18;
    if(c.format && rows.length) s.getRange(`${col}6:${col}${end}`).setNumberFormat(c.format);
    if(c.type==='date' && rows.length) s.getRange(`${col}6:${col}${end}`).setNumberFormat('dd/mm/yyyy');
    if(c.wrap && rows.length) s.getRange(`${col}6:${col}${end}`).format.wrapText=true;
  }
  if(rows.length) {
    s.tables.add(`A5:${last}${end}`,true,`Tabla${def.name.replace(/[^A-Za-z0-9]/g,'')}`);
    s.freezePanes.freezeRows(5);
    if(n>6) s.freezePanes.freezeColumns(1);
  }
  for(const rule of def.rules || []) {
    s.getRange(`${rule.column}6:${rule.column}${end}`).conditionalFormats.add('containsText', {text:rule.text,format:{fill:'#FFF0D5',font:{color:'#814C10'}}});
  }
  diagnostics.push({sheet:def.name,rows:rows.length,columns:n});
}
wb.recalculate();
const summary=await wb.inspect({kind:'table',range:`${spec.sheets[0].name}!A5:F18`,include:'values,formulas',tableMaxRows:14,tableMaxCols:6,maxChars:6000});
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},maxChars:2500});
for(const def of spec.sheets) {
  if(renderOnly && !renderOnly.split(',').includes(def.name)) continue;
  for(let i=0;i<(def.previews||['A1:F13']).length;i++) {
    const p=await wb.render({sheetName:def.name,range:(def.previews||['A1:F13'])[i],scale:1.3,format:'png'});
    await fs.writeFile(path.join(qaDir,`${def.name}_${i}.png`),new Uint8Array(await p.arrayBuffer()));
  }
}
const result=await SpreadsheetFile.exportXlsx(wb);
await result.save(output);
await fs.writeFile(path.join(qaDir,'revision_excel.json'),JSON.stringify({sheets:diagnostics,summary:summary.ndjson,errors:errors.ndjson},null,2));
console.log(JSON.stringify({output,sheets:diagnostics}));
