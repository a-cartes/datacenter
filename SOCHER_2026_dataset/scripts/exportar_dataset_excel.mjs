import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const out=path.join(root,'outputs/01a0d6c3-09cd-7aa3-903d-5ee59e65c071');
const prep=path.join(out,'preparacion');
const meta=JSON.parse(await fs.readFile(path.join(prep,'metadata.json'),'utf8'));
const wb=Workbook.create();
const panel=wb.worksheets.add('Panel horario');
const dict=wb.worksheets.add('Diccionario');
const colName=(index)=>{ let s=''; for(let n=index+1;n>0;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
panel.getRange('A1:BN1').values=[meta.headers];
let offset=1;
const dates=meta.headers.map((h,i)=>meta.types[h].startsWith('datetime')?i:-1).filter(i=>i>=0);
for(const filename of meta.chunks){
  const rows=JSON.parse(await fs.readFile(path.join(prep,filename),'utf8'));
  for(const row of rows)for(const i of dates)if(row[i]!==null)row[i]=new Date(row[i].includes('T')?row[i]:row[i]+'T00:00:00Z');
  panel.getRangeByIndexes(offset,0,rows.length,66).values=rows;
  offset+=rows.length;
  if((offset-1)%25000===0||offset===meta.rows+1)console.log(`Filas cargadas: ${offset-1}`);
}
const last=meta.rows+1;
panel.showGridLines=false;
panel.tabColor='#203B53';
panel.getRange(`A1:BN${last}`).format.font={name:'Arial',size:10,color:'#203040'};
panel.getRange(`A1:BN${last}`).format.rowHeight=20;
panel.getRange('A1:BN1').format={fill:'#203B53',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,verticalAlignment:'center'};
panel.getRange('A1:BN1').format.rowHeight=56;
for(let i=0;i<meta.headers.length;i++){
  const col=colName(i), name=meta.headers[i], type=meta.types[name];
  let width=24;
  if(i===0)width=14;
  else if(i===1)width=16;
  else if(name.includes('archivo'))width=65;
  else if(name.includes('nota'))width=70;
  else if(name.includes('nemotecnico')||name.includes('clave_barra'))width=43;
  else if(name.includes('estado')||name.includes('regimen')||name.includes('vinculo'))width=38;
  else if(name.includes('id'))width=32;
  panel.getRange(`${col}1:${col}${last}`).format.columnWidth=width;
  if(type.startsWith('datetime'))panel.getRange(`${col}2:${col}${last}`).setNumberFormat('yyyy-mm-dd');
  else if(type.toLowerCase().startsWith('float'))panel.getRange(`${col}2:${col}${last}`).setNumberFormat('0.000000');
  else if(type.toLowerCase().startsWith('int'))panel.getRange(`${col}2:${col}${last}`).setNumberFormat('0');
  else if(type==='str')panel.getRange(`${col}2:${col}${last}`).setNumberFormat('@');
}
panel.freezePanes.freezeRows(1);
panel.freezePanes.freezeColumns(4);
const table=panel.tables.add(`A1:BN${last}`,true,'PanelHorario');
table.showFilterButton=true;
dict.getRange('A1:E1').values=[['variable','definicion','unidad','tipo','n_nulos']];
dict.getRange('A2:E67').values=meta.definitions.map(d=>[d.variable,d.definicion,d.unidad||null,d.tipo,Number(d.n_nulos)]);
dict.showGridLines=false;
dict.tabColor='#448583';
dict.getRange('A1:E67').format.font={name:'Arial',size:11,color:'#203040'};
dict.getRange('A1:E67').format.verticalAlignment='center';
dict.getRange('A1:E67').format.wrapText=true;
dict.getRange('A1:E67').format.rowHeight=48;
dict.getRange('A1:E1').format={fill:'#203B53',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'}};
dict.getRange('A1:E1').format.rowHeight=28;
for(const [col,width]of [['A',42],['B',106],['C',18],['D',23],['E',15]])dict.getRange(`${col}1:${col}67`).format.columnWidth=width;
dict.getRange('E2:E67').setNumberFormat('#,##0');
dict.freezePanes.freezeRows(1);
dict.tables.add('A1:E67',true,'DiccionarioPanel').showFilterButton=true;
console.log('Formato completado.');
wb.recalculate();
const checks=[];
for(const range of ["'Panel horario'!A1:J4",`'Panel horario'!A${last-2}:J${last}`,'Diccionario!A1:E5'])checks.push((await wb.inspect({kind:'table',range,include:'values,formulas',tableMaxRows:5,tableMaxCols:10,maxChars:2500})).ndjson);
checks.push((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},maxChars:2000})).ndjson);
await fs.writeFile(path.join(prep,'inspeccion.txt'),checks.join('\n'));
for(const [sheetName,range,name]of [['Panel horario','A1:J7','panel'],['Diccionario','A1:E8','diccionario']]){
  const preview=await wb.render({sheetName,range,scale:1,format:'png'});
  await fs.writeFile(path.join(prep,`${name}.png`),new Uint8Array(await preview.arrayBuffer()));
}
console.log('Exportando Excel completo.');
const xlsx=await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(path.join(out,'Dataset_articulo.xlsx'));
console.log('Excel exportado.');
