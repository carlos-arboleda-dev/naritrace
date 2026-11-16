import { Component, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

/** Pantalla provisional para secciones del menú que aún no están construidas. */
@Component({
  selector: 'app-proximamente',
  standalone: true,
  template: `
    <div class="vacio">
      <h2>{{ titulo }}</h2>
      <p>Esta sección estará disponible muy pronto.</p>
    </div>
  `,
  styles: [`
    .vacio { padding: 3rem 0; }
    h2 { font-weight: 800; color: var(--nt-texto); }
    p { color: var(--nt-texto-suave); }
  `]
})
export class ProximamenteComponent {
  titulo = inject(ActivatedRoute).snapshot.data['titulo'] ?? 'Próximamente';
}
