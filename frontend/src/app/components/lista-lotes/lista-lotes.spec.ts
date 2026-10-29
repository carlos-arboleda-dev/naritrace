import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ListaLotes } from './lista-lotes';

describe('ListaLotes', () => {
  let component: ListaLotes;
  let fixture: ComponentFixture<ListaLotes>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListaLotes],
    }).compileComponents();

    fixture = TestBed.createComponent(ListaLotes);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
