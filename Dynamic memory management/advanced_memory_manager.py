# advanced_memory_manager.py

class Heap:
    """
    A custom Heap implementation that can function as a min-heap or a max-heap.
    It does not use the standard `heapq` library.
    The heap stores tuples, and comparison is based on the first element of the tuple.
    """
    def __init__(self, heap_type='min'):
        if heap_type not in ['min', 'max']:
            raise ValueError("heap_type must be 'min' or 'max'")
        self.heap = []
        self.heap_type = heap_type

    def _compare(self, a, b):
        """Compares two elements based on heap type."""
        if self.heap_type == 'min':
            return a < b
        else: # max-heap
            return a > b

    def _parent(self, i):
        return (i - 1) // 2

    def _left_child(self, i):
        return 2 * i + 1

    def _right_child(self, i):
        return 2 * i + 2

    def _swap(self, i, j):
        """Swaps two elements in the heap."""
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def _sift_up(self, i, size=0):
        """Moves an element up the heap to its correct position."""
        parent_index = self._parent(i)
        while i > 0 and self._compare(self.heap[i][0], self.heap[parent_index][0]):
            self._swap(i, parent_index)
            i = parent_index
            parent_index = self._parent(i)

    def _sift_down(self, i, size=0):
        """Moves an element down the heap to its correct position."""
        max_index = i
        left = self._left_child(i)
        if left < len(self.heap) and self._compare(self.heap[left][0], self.heap[max_index][0]):
            max_index = left

        right = self._right_child(i)
        if right < len(self.heap) and self._compare(self.heap[right][0], self.heap[max_index][0]):
            max_index = right

        if i != max_index:
            self._swap(i, max_index)
            self._sift_down(max_index)

    def push(self, item):
        """Adds an item to the heap."""
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)

    def pop(self):
        """Removes and returns the root item from the heap."""
        if not self.heap:
            return None
        
        root = self.heap[0]
        last_item = self.heap.pop()
        if self.heap:
            self.heap[0] = last_item
            self._sift_down(0)
        return root

    def remove(self, item):
        """Removes a specific item from the heap. O(n) search."""
        try:
            index = self.heap.index(item)
            last_item = self.heap.pop()
            
            # If the item to remove was the last one, we're done.
            if index == len(self.heap):
                return

            self.heap[index] = last_item
            # Decide whether to sift up or down
            parent_index = self._parent(index)
            if index > 0 and self._compare(self.heap[index][0], self.heap[parent_index][0]):
                self._sift_up(index)
            else:
                self._sift_down(index)
        except ValueError:
            # Item not found, could happen if merging already removed it.
            # Silently ignore for robustness in the memory manager context.
            pass

    def is_empty(self):
        """Checks if the heap is empty."""
        return len(self.heap) == 0

    def peek(self):
        """Returns the root item without removing it."""
        return self.heap[0] if self.heap else None

    def __len__(self):
        return len(self.heap)

    def find_best_fit(self, size):
        """Finds the smallest block that fits the size."""
        best_fit = None
        # A min-heap is naturally suited for this
        if self.heap_type == 'min':
            temp_storage = []
            while not self.is_empty():
                block = self.pop()
                if block[0] >= size:
                    best_fit = block
                    break
                temp_storage.append(block)
            
            # Restore other blocks
            if best_fit:
                self.push(best_fit) # put it back for now
            for item in temp_storage:
                self.push(item)
            return best_fit

        # For a max-heap, we'd have to search more extensively
        # This highlights why min-heap is 'best-fit'
        return None

# The MemoryManager and main function will be added in the next step.

class MemoryManager:
    """
    A simulation of a contiguous memory manager with multiple fit strategies.
    It uses the custom Heap class for best-fit and worst-fit algorithms.
    """
    def __init__(self, total_size):
        self.total_size = total_size
        self.next_id = 1
        
        # This dictionary holds all blocks, both allocated and free.
        # Key: block_id, Value: block_dictionary
        self.all_blocks = {}
        self.address_map = {} # New: For faster neighbor lookups
        
        # Create and add the first block
        initial_block = {
            'id': self.next_id,
            'size': total_size,
            'free': True,
            'start_address': 0
        }
        self.all_blocks[self.next_id] = initial_block
        self.address_map[0] = initial_block
        
        # Heaps for managing free blocks for different strategies
        self.min_heap = Heap(heap_type='min')
        self.max_heap = Heap(heap_type='max')
        
        # Add the initial free block to the heaps. Format: (size, start_address, id)
        initial_block_tuple = (total_size, 0, self.next_id)
        self.min_heap.push(initial_block_tuple)
        self.max_heap.push(initial_block_tuple)
        
        self.next_id += 1
        print(f"Initialized memory with a single block of {total_size} units.")
        self.display_memory()

    def display_memory(self):
        print("\n--- Memory Layout ---")
        # Sort blocks by start_address to visualize the contiguous memory space.
        blocks = sorted(self.all_blocks.values(), key=lambda b: b['start_address'])
        total_free = 0
        total_allocated = 0
        
        for block in blocks:
            status = "Free" if block['free'] else "Allocated"
            end_address = block['start_address'] + block['size'] - 1
            print(f"  ID: {block['id']:<3} | Status: {status:<9} | Size: {block['size']:<5} | Addr: {block['start_address']} -> {end_address}")
            if block['free']:
                total_free += block['size']
            else:
                total_allocated += block['size']
        
        print(f"\n> Total Allocated: {total_allocated}")
        print(f"> Total Free:      {total_free}")
        print(f"> Fragmentation (External): {total_free - self.max_heap.peek()[0] if not self.max_heap.is_empty() else 0}")
        print("---------------------\n")

    def to_dict(self):
        """Returns a dictionary representation of the memory state for API responses."""
        return {
            'total_size': self.total_size,
            'blocks': sorted(list(self.all_blocks.values()), key=lambda b: b['start_address'])
        }

    def _find_first_fit_block(self, size):
        # For first-fit, we iterate through blocks sorted by address
        blocks_by_address = sorted(self.all_blocks.values(), key=lambda b: b['start_address'])
        for block in blocks_by_address:
            if block['free'] and block['size'] >= size:
                return (block['size'], block['start_address'], block['id'])
        return None

    def allocate(self, size, strategy):
        if strategy not in ['best', 'worst', 'first']:
            print("Error: Invalid allocation strategy.")
            return

        print(f"Attempting to allocate {size} units using '{strategy}-fit'...")
        
        found_block_tuple = None
        
        if strategy == 'first':
            found_block_tuple = self._find_first_fit_block(size)
        
        elif strategy == 'best':
            found_block_tuple = self.min_heap.find_best_fit(size)
            if found_block_tuple:
                self.min_heap.remove(found_block_tuple)

        elif strategy == 'worst':
            # The largest block is at the root of the max-heap
            if not self.max_heap.is_empty() and self.max_heap.peek()[0] >= size:
                found_block_tuple = self.max_heap.pop()

        if not found_block_tuple:
            print(f"Error: No suitable block found for size {size}.")
            self.display_memory()
            return

        original_size, start_address, block_id = found_block_tuple
        
        # Remove the block from the *other* heap as well.
        if strategy == 'best':
            self.max_heap.remove(found_block_tuple)
        elif strategy == 'worst':
            self.min_heap.remove(found_block_tuple)
        elif strategy == 'first':
            self.min_heap.remove(found_block_tuple)
            self.max_heap.remove(found_block_tuple)

        block_to_alloc = self.all_blocks[block_id]
        remaining_size = original_size - size
        
        # --- Block Splitting ---
        # If the found block is larger than required, split it.
        # This reduces internal fragmentation if we were allocating fixed-size chunks,
        # but in this model, it creates a smaller external fragment.
        if remaining_size > 0:
            # Update the original block to be the allocated portion
            block_to_alloc['size'] = size
            block_to_alloc['free'] = False
            
            # Create a new block for the leftover free space
            new_block_start = start_address + size
            new_block_id = self.next_id
            self.all_blocks[new_block_id] = {
                'id': new_block_id, 
                'size': remaining_size, 
                'free': True, 
                'start_address': new_block_start
            }
            self.address_map[new_block_start] = self.all_blocks[new_block_id]
            # Add this new free block to our heaps
            new_block_tuple = (remaining_size, new_block_start, new_block_id)
            self.min_heap.push(new_block_tuple)
            self.max_heap.push(new_block_tuple)
            self.next_id += 1
        else: # Perfect fit
            block_to_alloc['free'] = False
        
        # Update address map for the allocated block
        del self.address_map[block_to_alloc['start_address']]
        
        print(f"Successfully allocated {size} units in block ID {block_id}.")
        self.display_memory()

    def find_block_at(self, address):
        """Finds a block at a specific start address."""
        # This is inefficient and for demonstration. A dict mapping start_address -> id would be better.
        for block in self.all_blocks.values():
            if block['start_address'] == address:
                return block
        return None

    def deallocate(self, block_id):
        try:
            block_id = int(block_id)
        except (ValueError, TypeError):
            print(f"Error: Invalid Block ID format: {block_id}.")
            return

        if block_id not in self.all_blocks:
            print(f"Error: Block ID {block_id} not found.")
            return

        block_to_free = self.all_blocks[block_id]
        if block_to_free['free']:
            print(f"Warning: Block ID {block_id} is already free.")
            return

        print(f"Deallocating block ID {block_id}...")
        block_to_free['free'] = True
        
        # --- Coalescing ---
        # Merge with next block if it's free
        next_block_start = block_to_free['start_address'] + block_to_free['size']
        if next_block_start in self.address_map:
            next_block = self.address_map[next_block_start]
            if next_block['free']:
                print(f"Merging with next block ID {next_block['id']}...")
                self.min_heap.remove((next_block['size'], next_block['start_address'], next_block['id']))
                self.max_heap.remove((next_block['size'], next_block['start_address'], next_block['id']))
                
                block_to_free['size'] += next_block['size']
                del self.all_blocks[next_block['id']]
                del self.address_map[next_block['start_address']]

        # Merge with previous block if it's free
        # This is complex without a reverse mapping, but we can search for it.
        # A more optimal solution would be a doubly-linked list of blocks.
        for b_id, b in list(self.all_blocks.items()):
            if b_id == block_to_free['id']:
                continue
            if b['start_address'] + b['size'] == block_to_free['start_address'] and b['free']:
                print(f"Merging with previous block ID {b['id']}...")
                self.min_heap.remove((b['size'], b['start_address'], b['id']))
                self.max_heap.remove((b['size'], b['start_address'], b['id']))

                b['size'] += block_to_free['size']
                del self.all_blocks[block_to_free['id']]
                del self.address_map[block_to_free['start_address']]
                block_to_free = b # The previous block is now the primary one
                break
        
        # Add the final (potentially merged) block back to free lists
        final_tuple = (block_to_free['size'], block_to_free['start_address'], block_to_free['id'])
        self.min_heap.push(final_tuple)
        self.max_heap.push(final_tuple)
        self.address_map[block_to_free['start_address']] = block_to_free
        
        print("Deallocation and coalescing complete.")
        self.display_memory()

def main():
    try:
        total_size = int(input("Enter total memory size: "))
        if total_size <= 0:
            raise ValueError
    except ValueError:
        print("Invalid size. Please enter a positive integer.")
        return
        
    mm = MemoryManager(total_size)
    strategy = 'best' # Default strategy

    while True:
        print(f"Current Strategy: '{strategy}-fit'. Choose an action:")
        print("  [1] Allocate a Single Memory Block")
        print("  [2] Allocate Multiple Memory Blocks")
        print("  [3] Deallocate Memory")
        print("  [4] Change Strategy (best, worst, first)")
        print("  [5] Display Memory")
        print("  [6] Exit")
        choice = input("> ").strip()

        if choice == '1':
            try:
                size = int(input("Enter size to allocate: "))
                if size <= 0:
                    raise ValueError
                mm.allocate(size, strategy)
            except ValueError:
                print("Invalid size. Please enter a positive integer.")
        elif choice == '2':
            try:
                num_blocks = int(input("Enter the number of blocks to allocate: "))
                if num_blocks <= 0:
                    raise ValueError
                for i in range(num_blocks):
                    try:
                        size = int(input(f"Enter size for block {i+1}: "))
                        if size <= 0:
                            raise ValueError
                        mm.allocate(size, strategy)
                    except ValueError:
                        print("Invalid size. Skipping this block.")
            except ValueError:
                print("Invalid number. Please enter a positive integer for the number of blocks.")
        elif choice == '3':
            block_id = input("Enter Block ID to deallocate: ")
            mm.deallocate(block_id)
        elif choice == '4':
            new_strategy = input("Enter new strategy (best, worst, first): ").strip().lower()
            if new_strategy in ['best', 'worst', 'first']:
                strategy = new_strategy
                print(f"Strategy changed to '{strategy}-fit'.")
            else:
                print("Invalid strategy.")
        elif choice == '5':
            mm.display_memory()
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()