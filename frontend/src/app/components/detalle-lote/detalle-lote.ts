import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, Validators, FormGroup } from '@angular/forms';
import { QRCodeComponent } from 'angularx-qrcode';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-detalle-lote',
  standalone: true,
  imports: [CommonModule, RouterLink, QRCodeComponent, ReactiveFormsModule],
  templateUrl: './detalle-lote.html',
  styleUrl: './detalle-lote.css'
})
export class DetalleLoteComponent implements OnInit {
  lote: any = null;
  movimientos: any[] = [];
  id!: number;
  
  // Formulario de movimientos
  formMovimiento: FormGroup;
  guardandoMovimiento = false;

  constructor(
    private route: ActivatedRoute,
    private api: ApiService,
    private cdr: ChangeDetectorRef,
    private fb: FormBuilder
  ) {
    this.formMovimiento = this.fb.group({
      tipo: ['cosecha', Validators.required],
      descripcion: ['', Validators.required],
      origen: [''],
      destino: ['']
    });
  }

  ngOnInit() {
    this.id = Number(this.route.snapshot.paramMap.get('id'));
    this.cargarLote();
    this.cargarMovimientos();
  }

  cargarLote() {
    this.api.getLote(this.id).subscribe(data => {
      this.lote = data;
      this.cdr.detectChanges();
    });
  }

  cargarMovimientos() {
    this.api.getMovimientos(this.id).subscribe((data: any) => {
      // Por si viene paginado
      this.movimientos = data.results ? data.results : data;
      this.cdr.detectChanges();
    });
  }

  publicar() {
    this.api.publicarLote(this.id).subscribe(() => {
      this.cargarLote(); 
    });
  }

  agregarMovimiento() {
    if (this.formMovimiento.invalid) return;
    this.guardandoMovimiento = true;

    const payload = {
      lote: this.id,
      ...this.formMovimiento.value
    };

    this.api.crearMovimiento(payload).subscribe({
      next: () => {
        this.formMovimiento.reset({ tipo: 'cosecha' });
        this.guardandoMovimiento = false;
        this.cargarMovimientos(); // Recargar la lista de movimientos
      },
      error: (err) => {
        console.error(err);
        this.guardandoMovimiento = false;
      }
    });
  }
}