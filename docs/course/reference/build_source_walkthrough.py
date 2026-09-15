#!/usr/bin/env python3
"""Refresh source-order execution notes; --check rejects stale checked-in notes.

Uses Python's AST and the Acorn already installed in the Enterprise checkout.
It does not import Odoo, execute customer code, or contact a provider.
"""
import argparse
import ast
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import tempfile

BEGIN = "<!-- BEGIN GENERATED SOURCE NOTES -->"
END = "<!-- END GENERATED SOURCE NOTES -->"
COURSE = Path(__file__).resolve().parent.parent

# These are reading boundaries, not assertions about every function's side effects.
PURPOSES = {
    "controllers": "HTTP boundary: follow decorators, identity and input validation before model calls. An auth=public route still needs its explicit authentication contract.",
    "phone_service_payment": "Money boundary: reserve one reference, retain its remote idempotency key, record the attempt outcome, and let the existing recovery job retry. See the authored payment sitting below.",
    "phone_service_order": "Ordinary purchase saga: authorization, provider submission and capture are separate steps, not one atomic transaction. Follow compensation and ambiguous-response handling.",
    "advanced_order": "Feature-specific sourcing request: parent status, comments and resulting ordinary orders remain distinct. Verify that this feature is present in your release before treating it as deployed.",
    "pbx_tenant_ops": "Provider choreography: translate customer-owned intent into Wazo resources and associations, including conflict adoption and scoped deletion. A local savepoint cannot undo a completed HTTP request.",
    "pbx_tenant": "Durable provisioning boundary: the tenant carries progress and provider identifiers; steps resume from recorded state. Separate customer ownership from explicit transport scope.",
    "wazo_api": "Wazo transport: explicit tenant/master scope and retry/error handling. Customer ownership is checked by the controller, not inferred by this transport.",
    "wazo_client": "REST vocabulary: collection commands and relation objects centralize URLs and association operations. A missing-resource probe is not a successful provisioning result.",
    "phone_service_api": "Customer capability facade: the broker endpoint and signed client identity are its trust boundary; it is not a Wazo passthrough.",
    "phone_service_event": "Event reconciliation: decode and deduplicate first, then derive records from stable identifiers. Duplicate and out-of-order delivery are not a linear UI script.",
    "voip_sound": "Audio boundary: generate a preview before saving, validate matching text/voice metadata, and distinguish synchronous upload from deferred deletion. See the authored audio sitting below.",
    "pbx_service": "Enterprise PBX vocabulary: delegates call broker capabilities. Only explicit postcommit registration defers execution; the deletion helper additionally rechecks that the row is gone.",
    "call_flow": "Routing compiler: the browser edits a graph; the server owns graph validity, resource ownership and conversion to bounded PBX destinations.",
    "cron": "Recovery machinery: read the selection domain, claim and progress handling together. Scheduled recovery does not imply every error has a retry job.",
    "telnyx": "Carrier boundary: read request, response normalization and webhook authentication separately. A local test does not prove provider replay semantics.",
    "wav": "Pure audio conversion: decode the format before transforming samples; verify channel, width and sample-rate assumptions against the nearest tests.",
    "static/src": "Browser boundary: locate registration/imports, then lifecycle, handlers and state updates. UI/SIP state and durable Odoo state are separate; read the XML sibling and nearest Hoot test.",
    "models": "Odoo model boundary: declarations define the ORM contract. Follow dependencies, constraints, batch create/write and explicit external calls. The transaction behavior must be read in this file.",
    "wizards": "Transient user journey: criteria, cached results, validation and submission are distinct states; changing a criterion can invalidate a prior result.",
    "tools": "Shared implementation helper: determine the caller's format and error assumptions before changing conversion or parsing behavior.",
}


def code(value):
    return "<code>" + html.escape(str(value)) + "</code>"


def expression(node):
    text = ast.unparse(node) if node is not None else "None"
    return text if len(text) <= 260 else text[:257] + "…"


def steps(body):
    """Explain visible control flow without claiming transitive or remote effects."""
    result = []
    for node in body:
        children = ""
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        if isinstance(node, ast.If):
            label = "Test " + code(expression(node.test)) + ". If true:"
            children = steps(node.body)
            if node.orelse:
                children += "<p>Otherwise:</p>" + steps(node.orelse)
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            label = ("Repeat while " + code(expression(node.test)) if isinstance(node, ast.While)
                     else "For each " + code(expression(node.target)) + " in " + code(expression(node.iter))) + ":"
            children = steps(node.body)
            if node.orelse:
                children += "<p>If the loop finishes without break:</p>" + steps(node.orelse)
        elif isinstance(node, (ast.Try, ast.TryStar)):
            label, children = "Try these operations:", steps(node.body)
            for handler in node.handlers:
                children += "<p>On " + code(expression(handler.type) if handler.type else "any exception") + ":</p>" + steps(handler.body)
            if node.orelse:
                children += "<p>If no exception escaped the try block:</p>" + steps(node.orelse)
            if node.finalbody:
                children += "<p>Finally, on normal or exceptional exit:</p>" + steps(node.finalbody)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            label = "Enter context " + code(", ".join(expression(item.context_expr) for item in node.items)) + "; its exit semantics matter:"
            children = steps(node.body)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            label = "Define callback " + code(node.name) + "; definition alone does not execute its body. Read its separate function card and its decorators."
        elif isinstance(node, ast.Return):
            label = "Return " + code(expression(node.value)) + "; this branch ends here."
        elif isinstance(node, ast.Raise):
            label = "Raise " + code(expression(node.exc) if node.exc else "the current exception") + "; follow the nearest applicable handler, not an assumed provider rollback."
        elif isinstance(node, ast.Assign):
            label = "Set " + code(" = ".join(expression(target) for target in node.targets)) + " from " + code(expression(node.value)) + "."
        elif isinstance(node, ast.AnnAssign):
            label = "Declare " + code(expression(node.target)) + " as " + code(expression(node.annotation)) + ", with value " + code(expression(node.value)) + "."
        elif isinstance(node, ast.Expr):
            if isinstance(node.value, (ast.Yield, ast.YieldFrom)):
                label = ("Delegate with " if isinstance(node.value, ast.YieldFrom) else "Yield ") + code(expression(node.value)) + "; suspend here until the caller resumes or throws an exception back. With @contextmanager, the caller's with-body runs at this point and its exceptions enter this generator."
            else:
                label = "Evaluate " + code(expression(node.value)) + "; follow the named callee for its effects."
        elif isinstance(node, ast.Match):
            label = "Match " + code(expression(node.subject)) + ":"
            for case in node.cases:
                children += "<p>Case " + code(expression(case.pattern)) + (" when " + code(expression(case.guard)) if case.guard else "") + ":</p>" + steps(case.body)
        else:
            label = "Execute " + code(expression(node)) + "."
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and any(isinstance(part, (ast.Yield, ast.YieldFrom)) for part in ast.walk(node)):
            label += " A yield suspends this generator before the assignment completes; resumption supplies its value or raises the caller's exception."
        result.append("<li>" + label + children + "</li>")
    return "<ol>" + "".join(result) + "</ol>" if result else "<p>No executable statements.</p>"


def python_functions(tree, prefix=""):
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            yield from python_functions(node, prefix + node.name + ".")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorators = ["@" + expression(item) for item in node.decorator_list]
            if isinstance(node, ast.AsyncFunctionDef):
                decorators.append("async function: execution is driven by awaiting/iteration, not definition")
            yield prefix + node.name, ast.unparse(node.args), ast.get_docstring(node), steps(node.body), decorators
            yield from python_functions(node, prefix + node.name + ".")
        else:
            yield from python_functions(node, prefix)


JS_READER = r"""
const fs = require('fs');
const {createRequire} = require('module');
const acorn = createRequire(process.argv[1] + '/package.json')('acorn');
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#x27;'}[c]));
const code = s => '<code>'+esc(s.length>260?s.slice(0,257)+'…':s)+'</code>';
const paths = JSON.parse(fs.readFileSync(0, 'utf8'));
const output = {};
for (const file of paths) {
 const source=fs.readFileSync(file,'utf8'), tree=acorn.parse(source,{ecmaVersion:'latest',sourceType:'module'});
 const text=n=>n?source.slice(n.start,n.end):'undefined';
 const explain=body=>'<ol>'+body.map(n=>{
  let label='', children='';
  if(n.type==='IfStatement'){label='Test '+code(text(n.test))+'. If true:';children=block(n.consequent);if(n.alternate)children+='<p>Otherwise:</p>'+block(n.alternate);}
  else if(n.type==='TryStatement'){label='Try these operations:';children=block(n.block);if(n.handler)children+='<p>On exception '+code(text(n.handler.param))+':</p>'+block(n.handler.body);if(n.finalizer)children+='<p>Finally:</p>'+block(n.finalizer);}
  else if(n.type==='DoWhileStatement'){label='Run the body at least once, then repeat while '+code(text(n.test))+':';children=block(n.body);}
  else if(n.type==='WhileStatement'){label='Repeat while '+code(text(n.test))+':';children=block(n.body);}
  else if(n.type==='ForStatement'){label='Initialize '+code(text(n.init))+', repeat while '+code(n.test?text(n.test):'true')+', updating with '+code(text(n.update))+':';children=block(n.body);}
  else if(['ForOfStatement','ForInStatement'].includes(n.type)){label='For each '+code(text(n.left))+(n.type==='ForOfStatement'?' of ':' in ')+code(text(n.right))+':';children=block(n.body);}
  else if(n.type==='SwitchStatement'){label='Select a case for '+code(text(n.discriminant))+':';children=n.cases.map(c=>'<p>'+ (c.test?'Case '+code(text(c.test)):'Default')+':</p>'+explain(c.consequent)).join('');}
  else if(n.type==='ReturnStatement')label='Return '+code(text(n.argument))+'; this branch ends here.';
  else if(n.type==='ThrowStatement')label='Throw '+code(text(n.argument))+'; follow the applicable catch handler.';
  else if(n.type==='BlockStatement'){label='Enter block:';children=explain(n.body);}
  else if(n.type==='VariableDeclaration')label='Bind '+n.declarations.map(d=>code(text(d.id))+(d.init?' from '+code(/FunctionExpression|ArrowFunctionExpression/.test(d.init.type)?'a callback (read its card)':text(d.init)):'')).join(', ')+'.';
  else if(n.type==='FunctionDeclaration')label='Define '+code(n.id?.name||'callback')+'; definition alone does not execute its body.';
  else label='Execute '+code(text(n))+'; await suspends this routine, and callbacks have their own execution time.';
  return '<li>'+label+children+'</li>';
 }).join('')+'</ol>';
 const block=n=>explain(n.type==='BlockStatement'?n.body:[n]);
 const functions=[], counts={};
 function walk(n,owner=[]){
  if(!n||typeof n!=='object')return;
  let next=owner;
  if(/ClassDeclaration|ClassExpression/.test(n.type)&&n.id)next=[...owner,n.id.name];
  if(n.type==='MethodDefinition'||n.type==='Property')next=[...owner,text(n.key)];
  if(n.type==='VariableDeclarator')next=[...owner,text(n.id)];
  if(/FunctionDeclaration|FunctionExpression|ArrowFunctionExpression/.test(n.type)){
   const base=[...owner,...(n.id?[n.id.name]:owner.length?[]:['callback'])].join('.');
   const occurrence=(counts[base]=(counts[base]||0)+1),name=base+(occurrence>1?' (callback '+occurrence+')':'');
   functions.push([name,n.params.map(text).join(', '),null,n.body.type==='BlockStatement'?explain(n.body.body):'<ol><li>Evaluate and return '+code(text(n.body))+'.</li></ol>',[]]);
   next=[...owner,n.id?.name||'callback'];
  }
  for(const [key,val] of Object.entries(n)){if(['start','end','type'].includes(key))continue;if(Array.isArray(val))val.forEach(v=>walk(v,next));else if(val&&typeof val==='object')walk(val,next);}
 }
 walk(tree);output[file]=functions;
}
console.log(JSON.stringify(output));
"""


def generate(workspace):
    roots = [("Enterprise VoIP", workspace / "master/enterprise/voip"),
             ("IAP Phone Service", workspace / "master/iap-apps/iap_services/phone_service")]
    files = [(label, root, path) for label, root in roots for path in sorted(root.rglob("*"))
             if path.is_file() and path.suffix in {".py", ".js"} and not {"tests", "lib", "vendor", "__pycache__"}.intersection(path.relative_to(root).parts)]
    if not all(root.is_dir() for _, root in roots):
        raise ValueError("Expected source checkouts beneath --workspace/master; no files were modified.")
    js_paths = [str(path) for _, _, path in files if path.suffix == ".js"]
    js = json.loads(subprocess.run(["node", "-e", JS_READER, str(workspace / "master/enterprise")],
                    input=json.dumps(js_paths), text=True, capture_output=True, check=True).stdout)
    digest = hashlib.sha256()
    chunks, count = [], 0
    for label, root, path in files:
        rel = path.relative_to(root).as_posix()
        digest.update((label + "/" + rel).encode())
        digest.update(path.read_bytes())
        funcs = list(python_functions(ast.parse(path.read_text()))) if path.suffix == ".py" else js[str(path)]
        count += len(funcs)
        purpose = next((value for key, value in PURPOSES.items() if key in rel), "Module wiring: imports and declarations connect this file to the manifest and registry. Read callers before changing its contract.")
        chunks.append("<details><summary>" + html.escape(label + " · " + rel) + "</summary><p>" + html.escape(purpose) + "</p>")
        for name, args, doc, body, decorators in funcs:
            anchor = "fn-" + hashlib.sha256((label + "/" + rel + ":" + name).encode()).hexdigest()[:16]
            chunks.append('<details id="' + anchor + '"><summary>' + code(name) + "</summary><p>Inputs and defaults: " + code(name + "(" + args + ")") + ".</p>")
            if decorators:
                chunks.append("<p>Decorators/execution contract: " + ", ".join(code(item) for item in decorators) + ". Read decorator implementations: they can wrap, register or replace this function.</p>")
            if doc:
                chunks.append("<p>Maintainer's function contract:</p><pre>" + html.escape(doc) + "</pre>")
            chunks.append("<p>Execution order (visible in this function, not inferred transitive effects):</p>" + body + "</details>")
        if not funcs:
            chunks.append("<p>No function body: read imports, model/field declarations and manifest entries as module wiring.</p>")
        chunks.append("</details>")
    for label, root in roots:
        resources = sorted(path.relative_to(root).as_posix() for path in root.rglob("*")
                           if path.is_file() and (path.suffix in {".xml", ".csv", ".scss"}
                           or ("tests" in path.relative_to(root).parts and path.suffix in {".py", ".js"})))
        digest.update(json.dumps(resources).encode())
        chunks.append("<details><summary>" + html.escape(label) + " · resources and companion tests</summary><p>XML wires views, actions and data; CSV declares access rights; SCSS styles the browser; tests freeze selected behaviors. Read each file beside its owning model or component, not as a second source of runtime authority.</p><p class=\"file-list\">" + ", ".join(code(name) for name in resources) + "</p></details>")
    return BEGIN + '\n<p class="muted">Source-derived companion: ' + str(len(files)) + " production Python/JavaScript files, " + str(count) + " function bodies. Fingerprint " + code(digest.hexdigest()) + ". No source line or commit anchors. Run the freshness check against your intended source checkouts.</p>\n" + "\n".join(chunks) + "\n" + END


def self_test(workspace):
    parsed = ast.parse("def charge(self, client):\n if self.bad:\n  raise ValueError('bad')\n try:\n  client.charge()\n except Exception:\n  return False\n else:\n  return True\n")
    functions = list(python_functions(parsed))
    assert len(functions) == 1 and functions[0][0] == "charge"
    body = functions[0][3]
    assert "If true" in body and "Raise" in body and "On" in body and "Return" in body
    assert "&lt;" in code("<script>") and "<script>" not in code("<script>")
    generator = list(python_functions(ast.parse("@contextmanager\ndef unit():\n try:\n  yield\n except Exception:\n  rollback()\n")))[0]
    assert generator[4] == ["@contextmanager"] and "suspend here" in generator[3] and "with-body" in generator[3]
    with tempfile.TemporaryDirectory(prefix="voip-source-parser-") as temp:
        fixture = Path(temp) / "loop.js"
        fixture.write_text("function next(){do {retry();} while (ids.has(id));}")
        parsed_js = json.loads(subprocess.run(["node", "-e", JS_READER, str(workspace / "master/enterprise")],
                              input=json.dumps([str(fixture)]), text=True, capture_output=True, check=True).stdout)
        assert "repeat while <code>ids.has(id)</code>" in parsed_js[str(fixture)][0][3]
    print("Source-note parser self-check passed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default_workspace = next((p for p in COURSE.parents if (p / "master/enterprise/voip").is_dir()), COURSE.parent)
    parser.add_argument("--workspace", type=Path, default=default_workspace)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test(args.workspace.resolve())
        return
    target = COURSE / "reference/source-walkthrough.html"
    current = target.read_text()
    if current.count(BEGIN) != 1 or current.count(END) != 1:
        raise ValueError("Expected exactly one generated source-notes region.")
    replacement = generate(args.workspace.resolve())
    updated = re.sub(re.escape(BEGIN) + r"[\s\S]*?" + re.escape(END), lambda _: replacement, current)
    if args.check:
        if updated != current:
            raise SystemExit("STALE source notes: refresh against the intended checkouts, review authored explanations, then mirror the course.")
        print("Source-note coverage and freshness check passed.")
    else:
        target.write_text(updated)
        print("Refreshed", target)


if __name__ == "__main__":
    main()
