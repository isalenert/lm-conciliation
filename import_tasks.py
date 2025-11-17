#!/usr/bin/env python3
"""
Script para importar tarefas do CSV para GitHub Issues
"""
import csv
import subprocess

def check_gh_cli():
    """Verifica se GitHub CLI está instalado"""
    try:
        subprocess.run(['gh', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ GitHub CLI não está instalado!")
        return False

def import_tasks(csv_file='tasks.csv'):
    """Importa tarefas do CSV para GitHub"""
    
    if not check_gh_cli():
        return
    
    print("🚀 Importando tarefas para o GitHub...")
    print()
    
    stats = {'done': 0, 'in-progress': 0, 'todo': 0, 'total': 0}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            status = row['status']
            title = row['title']
            description = row['description']
            labels = row['labels'].split(';')
            phase = row.get('phase', '').strip()
            
            # Montar corpo da issue
            body = f"{description}\n\n"
            body += f"**Status:** {status}\n"
            if phase:
                body += f"**Fase:** {phase}\n"
            
            # Labels como string
            labels_str = ','.join(labels)
            
            # Comando para criar issue
            cmd = [
                'gh', 'issue', 'create',
                '--title', title,
                '--body', body,
                '--label', labels_str
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                issue_url = result.stdout.strip()
                issue_number = issue_url.split('/')[-1]
                
                # Se for concluída, fechar imediatamente
                if status == 'done':
                    subprocess.run(['gh', 'issue', 'close', issue_number, '--reason', 'completed'], 
                                   capture_output=True, check=True)
                    print(f"✅ {title}")
                elif status == 'in-progress':
                    print(f"🔄 {title}")
                else:
                    print(f"📝 {title}")
                
                stats[status] += 1
                stats['total'] += 1
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Erro: {title}")
                if e.stderr:
                    print(f"   {e.stderr}")
    
    print()
    print("📊 Resumo:")
    print(f"   ✅ Concluídas: {stats['done']}")
    print(f"   🔄 Em progresso: {stats['in-progress']}")
    print(f"   📝 A fazer: {stats['todo']}")
    print(f"   📈 Total: {stats['total']}")
    print()
    print("🎉 Importação concluída!")
    print("👉 https://github.com/isalenert/lm-conciliation/issues")

if __name__ == '__main__':
    import_tasks()
