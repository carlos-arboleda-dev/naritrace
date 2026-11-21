import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { PanelApiService } from '../../services/panel-api';
import { IconComponent } from '../icon/icon';
import { fechaCorta } from '../admin-resumen/admin-resumen';

const PESTANAS = [
  { v: 'por_recibir', t: 'Por recibir' }, { v: 'custodia', t: 'En custodia' },
  { v: 'transito', t: 'En tránsito' }, { v: 'entregados', t: 'Entregados' },
];

/** Inventario (lotes por etapa) e Historial (movimientos propios) del distribuidor. */
@Component({
  selector: 'app-distribuidor-lista',
  standalone: true,
  imports: [IconComponent],
  templateUrl: './distribuidor-lista.html',
  styleUrl: './distribuidor-lista.css'
})
export class DistribuidorListaComponent implements OnInit {
  private api = inject(PanelApiService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  modo = this.route.snapshot.data['modo'] as 'inventario' | 'historial';
  pestanas = PESTANAS;
  vista = signal(this.route.snapshot.queryParamMap.get('vista') || 'custodia');
  buscar = signal('');
  tipo = signal('');
  filas = signal<any[]>([]);
  cargando = signal(true);
  error = signal('');
  fechaCorta = fechaCorta;
  private temporizador: ReturnType<typeof setTimeout> | undefined;
  titulo = computed(() => this.modo === 'inventario' ? 'Inventario' : 'Historial');

  ngOnInit() { this.cargar(); }

  cargar() {
    this.cargando.set(true); this.error.set('');
    const listo = (f: any[]) => { this.filas.set(f); this.cargando.set(false); };
    const fallo = () => { this.error.set('No pudimos cargar la información.'); this.cargando.set(false); };
    if (this.modo === 'inventario') this.api.distLotes(this.vista(), this.buscar()).subscribe({ next: listo, error: fallo });
    else this.api.distHistorial(this.tipo()).subscribe({ next: listo, error: fallo });
  }

  cambiarVista(v: string) { this.vista.set(v); this.cargar(); }
  alBuscar(v: string) { this.buscar.set(v); clearTimeout(this.temporizador); this.temporizador = setTimeout(() => this.cargar(), 300); }
  cambiarTipo(v: string) { this.tipo.set(v); this.cargar(); }
  operar(codigo: string) { this.router.navigate(['/dashboard/resumen'], { queryParams: { codigo } }); }
  etiqueta(a: string) { return a === 'recibir' ? 'Recibir' : a === 'despachar' ? 'Despachar' : 'Entregar'; }
}
